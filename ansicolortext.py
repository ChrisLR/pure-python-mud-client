# author: stefaan.himpe@gmail.com
# license: MIT
import re
import tkinter


class AnsiColorText(tkinter.Text):
    """
    class to convert text with ansi color codes to 
    text with tkinter color tags
    
    for now we ignore all but the simplest color directives
    see http://www.termsys.demon.co.uk/vtansi.htm for a list of
    other directives
    
    it has not been thoroughly tested, but it works well enough for demonstration purposes
    """
    foreground_colors = {
        'bright': {
            b'30': 'Grey',
            b'31': 'Red',
            b'32': 'Green',
            b'33': 'Brown',
            b'34': 'Blue',
            b'35': 'Purple',
            b'36': 'Cyan',
            b'37': 'White'
        },
        'dim': {
            b'30': 'DarkGray',
            b'31': 'LightRed',
            b'32': 'LightGreen',
            b'33': 'Yellow',
            b'34': 'LightBlue',
            b'35': 'Magenta',
            b'36': 'Pink',
            b'37': 'White'
        }
    }

    background_colors = {
        'bright': {
            b'40': 'Black',
            b'41': 'Red',
            b'42': 'Green',
            b'43': 'Brown',
            b'44': 'Blue',
            b'45': 'Purple',
            b'46': 'Cyan',
            b'47': 'White'
        },
        'dim': {
            b'40': 'DarkGray',
            b'41': 'LightRed',
            b'42': 'LightGreen',
            b'43': 'Yellow',
            b'44': 'LightBlue',
            b'45': 'Magenta',
            b'46': 'Pink',
            b'47': 'White'
        }
    }

    # define some regexes which will come in handy in filtering
    # out the ansi color codes
    color_pat = re.compile(b"\x01?\x1b\[([\d+;]*?)m\x02?")
    inner_color_pat = re.compile(b"^(\d+;?)+$")

    def __init__(self, parent):
        """
        initialize our specialized tkinter Text widget
        """
        tkinter.Text.__init__(self, parent)
        self.tag = None
        self.bright = None
        self.foreground_color = None
        self.background_color = None
        self.known_tags = set([])
        self.configure(background="Black")
        # register a default color tag
        self.register_tag("30", "White", "Black")
        self.reset_to_default_attribs()

    def reset_to_default_attribs(self):
        self.tag = '30'
        self.bright = 'bright'
        self.foreground_color = 'White'
        self.background_color = 'Black'

    def register_tag(self, txt, foreground, background):
        """
        register a tag with name txt and with given
        foreground and background color
        """
        self.tag_config(txt, foreground=foreground, background=background)
        self.known_tags.add(txt)

    def write(self, text, is_editable=False):
        """
        add text to the text widget
        """
        # first split the text at color codes, stripping stuff like the <ESC>
        # and \[ characters and keeping only the inner "0;23"-like codes
        segments = AnsiColorText.color_pat.split(text)
        if segments:
            for text in segments:
                text = text.replace(b'\r', b'')
                # a segment can be regular text, or it can be a color pattern
                if AnsiColorText.inner_color_pat.match(text):
                    # if it's a color pattern, check if we already have
                    # registered a tag for it
                    if text not in self.known_tags:
                        # if tag not yet registered,
                        # extract the foreground and background color
                        # and ignore the other things
                        parts = text.split(b";")
                        for part in parts:
                            if part in AnsiColorText.foreground_colors[self.bright]:
                                self.foreground_color = AnsiColorText.foreground_colors[self.bright][part]
                            elif part in AnsiColorText.background_colors[self.bright]:
                                self.background_color = AnsiColorText.background_colors[self.bright][part]
                            else:
                                for ch in part:
                                    if ch == b'0':
                                        # reset all attributes
                                        self.reset_to_default_attribs()
                                    if ch == b'1':
                                        # define bright colors
                                        self.bright = 'bright'
                                    if ch == b'2':
                                        # define dim colors
                                        self.bright = 'dim'

                        self.register_tag(text,
                                          foreground=self.foreground_color,
                                          background=self.background_color)
                    # remember that we switched to this tag
                    self.tag = text
                elif text == b'':
                    # reset tag to black
                    self.tag = b'30'  # black
                else:
                    # no color pattern, insert text with the currently selected
                    # tag
                    self.insert(tkinter.END, text, self.tag)
