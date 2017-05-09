from enum import Enum


class TelnetEnum(Enum):
        # escape
        InterpretAsCommand = 255,

        # commands
        SubnegotiationEnd = 240,
        NoOperation = 241,
        DataMark = 242,
        Break = 243,
        InterruptProcess = 244,
        AbortOutput = 245,
        AreYouThere = 246,
        EraseCharacter = 247,
        EraseLine = 248,
        GoAhead = 249,
        SubnegotiationBegin = 250,
        CarriageReturn = 13,

        # negotiation
        WILL = 251,
        WONT = 252,
        DO = 253,
        DONT = 254,

        # options (common)
        SuppressGoAhead = 3,
        Status = 5,
        Echo = 1,
        TimingMark = 6,
        TerminalType = 24,
        TerminalSpeed = 32,
        RemoteFlowControl = 33,
        LineMode = 34,
        EnvironmentVariables = 36,
        NAWS = 31,

        # options (MUD-specific)
        MSDP = 69,
        MXP = 91,
        MCCP1 = 85,
        MCCP2 = 86,
        MSP = 90