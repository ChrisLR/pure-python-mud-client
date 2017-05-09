"""
Original Code from https://www.codeproject.com/Articles/177846/MUD-Client-Essentials
Original Author: Ryan Hamshire
Ported to python by: Chris LR
"""
from telnet.enum import TelnetEnum


class TelnetParser(object):
    def __init__(self, socket, input_queue, output_queue):
        self.socket = socket
        self.input_queue = input_queue
        self.output_queue = output_queue

    def handle_and_remove_telnet_bytes(self, buffer, received_count, telnet_messages):
        """
        :param buffer: Stream of bytes to handle
        :param received_count: How many bytes received
        :param telnet_messages: List to hold a report of any telnet control sequences received or sent
        :return: Parsed content.
        """
        #

        # list to hold any bytes which aren't telnet bytes (which will be most of the bytes)
        content_bytes = []

        # We'll scan for telnet control sequences.
        # Anything NOT a telnet control sequence will be
        # added to the content_bytes list for later processing.
        current_index = 0
        while current_index < received_count:
            # search for an IAC, which may signal the beginning of a telnet message
            while current_index < received_count and buffer[current_index] != TelnetEnum.InterpretAsCommand.value:
                content_bytes.append(buffer[current_index])
                current_index += 1

            # if at the end of the data, stop.
            # otherwise we've encountered an IAC
            # and there should be at least one more byte here
            if current_index + 1 >= received_count:
                break

            # read the next byte
            second_byte = buffer[current_index]

            # if another IAC, then this was just sequence IAC IAC,
            # which is the escape sequence to represent byte value 255 (=IAC)
            # in the content stream
            if second_byte == bytes(TelnetEnum.InterpretAsCommand.value):
                # write byte value 255 to the content stream and move on
                content_bytes.append(second_byte)
            # Otherwise we have a "real" telnet sequence,
            # where the second byte is a command or negotiation
            else:
                # start building a string representation of this message, to be reported to the caller
                # caller might want to show this info to the user always, or optionally for debugging purposes
                string_version_of_message = ""

                # also build a string version of the response ( if any)
                string_version_of_response = ""

                # DO
                if second_byte == bytes(TelnetEnum.DO.value):
                    string_version_of_message += "DO "

                    # what are we being told to do?
                    current_index += 1
                    if current_index == received_count:
                        break

                    third_byte = buffer[current_index]
                    string_version_of_message += self.interpret_byte_as_telnet(third_byte)

                    # if NAWS(negotiate about window size)
                    if third_byte == bytes(TelnetEnum.NAWS.value):
                        # on connection, we offered to negotiate about window size.
                        # so this is a "go ahead and negotiate" response.
                        # so then, send information about client window size per the NAWS protocol
                        # we're lieing to server by telling it a ridiculously large size,
                        # so that it won' t do line breaking or paging for us(annoying!)
                        bytes_to_send = bytearray((
                            bytes(TelnetEnum.sub_negotiationBegin.value),
                            bytes(31), 254, 254, 254, 254,
                            bytes(TelnetEnum.InterpretAsCommand.value),
                            bytes(TelnetEnum.sub_negotiationEnd.value)
                        ))
                        string_version_of_response += self.send_telnet_bytes(bytes_to_send)
                    # everything else the server might ask us to do is unsupported by us
                    else:
                        string_version_of_message += self.interpret_byte_as_telnet(third_byte)
                        # sorry, i won't do whatever "that thing you said to do" was
                        string_version_of_response += self.send_telnet_bytes(
                            bytes_to_send=bytearray((
                                bytes(TelnetEnum.InterpretAsCommand.value),
                                bytes(TelnetEnum.WONT.value),
                                third_byte
                            )))
                # DON'T
                elif second_byte == bytes(TelnetEnum.DONT.value):
                    string_version_of_message += "DONT "
                    current_index += 1
                    if current_index == received_count:
                        break

                    third_byte = buffer[current_index]
                    string_version_of_message += self.interpret_byte_as_telnet(third_byte)

                    # whatever you want me to stop doing, that's no problem because i wasn' t going to do it anyway
                    string_version_of_response += self.send_telnet_bytes(
                        bytearray((bytes(TelnetEnum.WONT.value), third_byte)))

                # WILL
                elif second_byte == bytes(TelnetEnum.WILL.value):
                    string_version_of_message += "WILL "

                    # find out what the server is willing to do
                    current_index += 1
                    if current_index == received_count:
                        break
                    third_byte = buffer[current_index]
                    string_version_of_message += self.interpret_byte_as_telnet(third_byte)

                    # anything the server offers to do for us, we'll tell it not to because we don't know what it is
                    string_version_of_response += self.send_telnet_bytes(
                        bytearray((bytes(TelnetEnum.DONT.value), third_byte)))

                # WONT
                elif second_byte == bytes(TelnetEnum.WONT.value):
                    string_version_of_message += "WONT "

                    # find out what the server is NOT willing to do
                    current_index += 1
                    if current_index == received_count:
                        break
                    third_byte = buffer[current_index]

                    string_version_of_message += self.interpret_byte_as_telnet(third_byte)

                    # because we haven 't asked the server to DO anything,
                    # should not expect to receive any WONT
                    # however if we do receive a WONT,
                    # respond with a DONT to confirm that the server can go ahead
                    # and NOT do that thing it doesn't want to do
                    string_version_of_response += self.send_telnet_bytes(
                        bytearray((bytes(TelnetEnum.DONT.value), third_byte)))

                # sub_negotiations
                elif second_byte == bytes(TelnetEnum.SubnegotiationBegin.value):
                    string_version_of_message += "SB "
                    sub_negotiation_bytes = []

                    # read until an IAC followed by an SE
                    while current_index < received_count - 1 and not (
                            buffer[current_index] == bytes(TelnetEnum.InterpretAsCommand.value)
                            and buffer[current_index] == bytes(TelnetEnum.sub_negotiationEnd.value)):
                        sub_negotiation_bytes.append(buffer[current_index])
                        current_index += 1

                    sub_negotiation_bytes_array = bytearray(sub_negotiation_bytes)

                    # append the content of the sub_negotiation to the incoming message report string
                    string_version_of_message += str(sub_negotiation_bytes_array)

                    # append the sub_negotiation end
                    string_version_of_message += " SE"

                # any other telnet message
                else:
                    # try to convert it to a known message via the enum defined above
                    string_version_of_message += self.interpret_byte_as_telnet(second_byte)

                # report the control sequence we found, if any
                message_to_report = str(string_version_of_message)
                if not message_to_report:
                    telnet_messages.append("RECV: " + str(message_to_report))

                # report the response message sent, if any
                response_to_report = str(string_version_of_response)
                if not response_to_report:
                    telnet_messages.append("SEND: " + str(string_version_of_response))
            current_index += 1

        return bytes(content_bytes)

    @staticmethod
    def interpret_byte_as_telnet(byte):
        # try to convert the byte value to a string representation based on the Telnet enumeration
        friendly_name = None
        for enum in TelnetEnum:
            if enum.value == byte:
                friendly_name = enum
                break
        # if failed, just show the byte's numerical value in brackets, like [254]
        if not friendly_name:
            friendly_name = '[{}]'.format(byte)

        return friendly_name.name

    def send_telnet_bytes(self, bytes_to_send):
        # if not connected, do nothing
        if not self.socket:
            return ""

        # send IAC
        self.output_queue.put(bytes(TelnetEnum.InterpretAsCommand.value))

        # send the specified bytes
        self.output_queue.put(bytes_to_send)

        # start building a string to report to the caller
        report_message = ""

        for byte in bytes_to_send:
            # convert the byte value to something readable, 
            # and append it to the report string
            report_message += self.interpret_byte_as_telnet(byte) + " "

        return str(report_message)
