import xml.etree.cElementTree as ET

import click
from pathlib2 import Path


def ytt_time2str(t):
    ms = t % 1000 // 10
    s = t // 1000
    m = s // 60
    h = m // 60
    m = m % 60
    s = s % 60
    str = '{:0>2}:{:0>2}:{:0>2}.{:0>2}'.format(h, m, s, ms)
    return str


def color_ytt2ass(color, alpha=255):
    alpha = int(255 - alpha)
    alpha = '{:0>2}'.format(hex(alpha).split('x')[-1].upper())
    blue = color[-2:]
    green = color[-4:-2]
    red = color[-6:-4]
    return '&H{}{}{}{}'.format(alpha, blue, green, red)


class YttDoc:
    def __init__(self, height=1080, width=1920):
        self.pen_list = []
        self.ws_list = []
        self.wp_list = []
        self.subtitle_list = []
        self.v = height
        self.h = width
    
    @staticmethod
    def from_ytt(file_path):
        doc = YttDoc()
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        
        head = root[0]
        body = root[1]
        
        for element in head:
            if element.tag == 'pen':
                doc.add_pen(**element.attrib)
            elif element.tag == 'ws':
                doc.add_ws(**element.attrib)
            elif element.tag == 'wp':
                doc.add_wp(**element.attrib)
        
        for element in body:
            if element.text is not None:
                doc.add_subtitle(**element.attrib, text=element.text)
            else:
                for sub_element in element:
                    if len(sub_element.attrib) > 0:
                        doc.add_subtitle(**element.attrib, **sub_element.attrib, text=sub_element.text)
        return doc
    
    def to_ass_doc(self):
        ass_doc = AssDoc(height=self.h, width=self.v)
        self._gen_ass_style(ass_doc)
        
        for sub in self.subtitle_list:
            Start = ytt_time2str(sub.start_time)
            End = ytt_time2str(sub.start_time + sub.duration)
            
            style_num = self.get_pen_list_num(sub.pen.id) * len(self.wp_list) + self.get_wp_list_num(sub.wp.id)
            StyleName = 'style-{:0>4}'.format(style_num)
            style = ass_doc.get_style(StyleName)
            
            sub.text = str.replace(sub.text, '\n', '\\N')
            pos_h = self.h * sub.wp.pos_h // 100
            if pos_h - style.MarginL < 0:
                pos_h += style.MarginL
            elif pos_h + style.MarginR > self.h:
                pos_h -= style.MarginR
            
            pos_v = self.v * int(sub.wp.pos_v) // 100
            if pos_v - style.MarginV < 0:
                pos_v += style.MarginV
            elif pos_v + style.MarginV > self.v:
                pos_v -= style.MarginV
            
            pos = '{{\\pos({},{})}}'.format(pos_h, pos_v)
            Text = pos + sub.text
            
            ass_doc.add_subtitle(Start=Start, End=End, Style=StyleName, Text=Text)
        
        return ass_doc
    
    def _gen_ass_style(self, ass_doc):
        num = 0
        for pen in self.pen_list:
            for wp in self.wp_list:
                ass_style = AssDoc.AssStyle()
                if pen.bold == 1:
                    ass_style.Bold = -1
                if pen.italic == 1:
                    ass_style.Italic = -1
                if pen.under_line == 1:
                    ass_style.Underline = -1
                if pen.shadow_outline_type == 3:
                    ass_style.Outline = 1
                elif pen.shadow_outline_type == 4:
                    ass_style.BorderStyle = 1
                    ass_style.Outline = 0
                    ass_style.Shadow = 4
                else:
                    ass_style.BorderStyle = 3
                    ass_style.Shadow = 1
                
                p = wp.anchor_point
                ass_style.Alignment = 7 + p % 3 - p // 3 * 3
                
                ass_style.PrimaryColour = color_ytt2ass(pen.font_color, pen.font_openness)
                ass_style.OutlineColour = color_ytt2ass(pen.shadow_outline_color)
                ass_style.BackColour = color_ytt2ass(pen.bg_color, pen.bg_openness)
                
                # if pen.shadow_outline_type == 4:
                #     ass_style.PrimaryColour = color_ytt2ass(pen.font_color, 255 - pen.font_openness)
                #     ass_style.BackColour = color_ytt2ass(pen.bg_color, 255 - pen.bg_openness)
                
                ass_style.MarginL = 50
                ass_style.MarginR = 50
                ass_style.MarginV = 25
                
                base_font_size = 56
                factor = ((pen.font_size - 100) / 4) / 100 + 1
                ass_style.Fontsize = round(base_font_size * factor)
                
                ass_style.Name = 'style-{:0>4}'.format(num)
                num += 1
                
                ass_doc.add_style(ass_style)
    
    def add_pen(self, **kwargs):
        self.pen_list.append(self.pen(**kwargs))
    
    def add_ws(self, **kwargs):
        self.ws_list.append(self.ws(**kwargs))
    
    def add_wp(self, **kwargs):
        self.wp_list.append(self.wp(**kwargs))
    
    def add_subtitle(self, **kwargs):
        self.subtitle_list.append(self.subtitle(**kwargs, doc=self))
    
    def get_pen(self, idx):
        for pen in self.pen_list:
            if pen.id == idx:
                return pen
    
    def get_pen_list_num(self, idx):
        for i in range(len(self.pen_list)):
            if self.pen_list[i].id == idx:
                return i
    
    def get_ws(self, idx):
        for ws in self.ws_list:
            if ws.id == idx:
                return ws
    
    def get_wp(self, idx):
        for wp in self.wp_list:
            if wp.id == idx:
                return wp
    
    def get_wp_list_num(self, idx):
        for i in range(len(self.wp_list)):
            if self.wp_list[i].id == idx:
                return i
    
    class pen:
        def __init__(self, id=0, i=0, b=0, u=0, fs=4, fc='#FEFEFE', bc='#000000', fo=255, bo=0, et=0, ec='#000000',
                     sz=100):
            self.id = int(id)
            self.italic = int(i)
            self.bold = int(b)
            self.under_line = int(u)
            self.font = int(fs)
            self.font_color = fc
            self.bg_color = bc
            self.font_openness = int(fo)
            self.bg_openness = int(bo)
            self.shadow_outline_type = int(et)
            self.shadow_outline_color = ec
            self.font_size = int(sz)
    
    class ws:
        def __init__(self, id=0, ju=0, pd=0, sd=0):
            self.id = int(id)
            self.align = int(ju)
            self.vert = int(pd)
            self.orient = int(sd)
    
    class wp:
        def __init__(self, id=0, ap=0, ah=0, av=0):
            self.id = int(id)
            self.anchor_point = int(ap)
            self.pos_h = int(ah)
            self.pos_v = int(av)
    
    class subtitle:
        def __init__(self, t=0, d=0, p=0, ws=0, wp=0, text='', doc=None):
            self.start_time = int(t)
            self.duration = int(d)
            self.pen = doc.get_pen(int(p))
            self.ws = doc.get_ws(int(ws))
            self.wp = doc.get_wp(int(wp))
            self.text = text


class AssDoc:
    def __init__(self, height=1080, width=1920):
        self.style_list = []
        self.subtitle_list = []
        self.height = height
        self.width = width
        
        self.ignore_blod = False
    
    def add_style(self, style):
        self.style_list.append(style)
    
    def add_subtitle(self, **kwargs):
        self.subtitle_list.append(self.subtitle(**kwargs))
    
    def get_style(self, style_name):
        for style in self.style_list:
            if style.Name == style_name:
                return style
    
    def output(self, file_path):
        with open(file_path, 'w', encoding='UTF-8') as f:
            ass_str = []
            ass_str.append('[Script Info]\n')
            ass_str.append('; Script generated by ytt2ass\n')
            ass_str.append('; https://github.com/nitsaick/ytt2ass\n')
            ass_str.append('ScriptType: v4.00+\n')
            ass_str.append('PlayResX: {}\n'.format(self.height))
            ass_str.append('PlayResY: {}\n'.format(self.width))
            ass_str.append('\n')
            
            ass_str.append('[V4+ Styles]\n')
            ass_str.append(
                'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, '
                'Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
                'Alignment, MarginL, MarginR, MarginV, Encoding\n')
            
            for style in self.style_list:
                ass_str.append('Style: {},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n' \
                               .format(style.Name, style.Fontname, style.Fontsize,
                                       style.PrimaryColour, style.SecondaryColour,
                                       style.OutlineColour, style.BackColour, 0 if self.ignore_blod else style.Bold,
                                       style.Italic, style.Underline, style.StrikeOut, style.ScaleX,
                                       style.ScaleY, style.Spacing, style.Angle, style.BorderStyle,
                                       style.Outline, style.Shadow, style.Alignment, style.MarginL,
                                       style.MarginR, style.MarginV, style.Encoding))
            
            ass_str.append('\n[Events]\n')
            ass_str.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
            
            for subtitle in self.subtitle_list:
                ass_str.append('Dialogue: {},{},{},{},{},{},{},{},{},{}\n' \
                               .format(subtitle.Layer, subtitle.Start, subtitle.End, subtitle.Style, subtitle.Name,
                                       subtitle.MarginL, subtitle.MarginR, subtitle.MarginV, subtitle.Effect,
                                       subtitle.Text))
            
            f.writelines(ass_str)
    
    class AssStyle:
        def __init__(self, Name='Default', Fontname='FZLanTingHei-R-GBK', Fontsize=56,
                     PrimaryColour='&H00FFFFFF', SecondaryColour='&H00000000',
                     OutlineColour='&H00000000', BackColour='&H00000000',
                     Bold=0, Italic=0, Underline=0, StrikeOut=0,
                     ScaleX=100, ScaleY=100, Spacing=0, Angle=0,
                     BorderStyle=1, Outline=0, Shadow=0, Alignment=2,
                     MarginL=10, MarginR=10, MarginV=10, Encoding=1):
            self.Name = Name
            self.Fontname = Fontname
            self.Fontsize = int(Fontsize)
            self.PrimaryColour = PrimaryColour
            self.SecondaryColour = SecondaryColour
            self.OutlineColour = OutlineColour
            self.BackColour = BackColour
            self.Bold = int(Bold)
            self.Italic = int(Italic)
            self.Underline = int(Underline)
            self.StrikeOut = int(StrikeOut)
            self.ScaleX = int(ScaleX)
            self.ScaleY = int(ScaleY)
            self.Spacing = int(Spacing)
            self.Angle = int(Angle)
            self.BorderStyle = int(BorderStyle)
            self.Outline = int(Outline)
            self.Shadow = int(Shadow)
            self.Alignment = int(Alignment)
            self.MarginL = int(MarginL)
            self.MarginR = int(MarginR)
            self.MarginV = int(MarginV)
            self.Encoding = int(Encoding)
    
    class subtitle:
        def __init__(self, Layer=0, Start='00:00:00.00', End='00:00:00.00', Style='Default',
                     Name='', MarginL=0, MarginR=0, MarginV=0, Effect='', Text=''):
            self.Layer = int(Layer)
            self.Start = Start
            self.End = End
            self.Style = Style
            self.Name = Name
            self.MarginL = int(MarginL)
            self.MarginR = int(MarginR)
            self.MarginV = int(MarginV)
            self.Effect = Effect
            self.Text = Text


@click.command()
@click.option('-i', '--input', help='Input youtube timedtext xml filename',
              type=click.Path(exists=True, file_okay=True, resolve_path=True), required=True)
@click.option('-o', '--output', help='Output ASS filename',
              type=click.Path(file_okay=True, resolve_path=True), required=True)
def main(input, output):
    ytt_file = Path(input)
    ass_file = Path(output)
    
    ytt_doc = YttDoc.from_ytt(ytt_file)
    ass_doc = ytt_doc.to_ass_doc()
    ass_doc.output(ass_file)


if __name__ == '__main__':
    main()
