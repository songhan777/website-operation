from pathlib import Path
import re, html, json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('YaHei',r'C:\Windows\Fonts\msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold',r'C:\Windows\Fonts\msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('YaHei',normal='YaHei',bold='YaHeiBold',italic='YaHei',boldItalic='YaHeiBold')
W,H=A4
M=48
CW=W-2*M
S={
 'title':ParagraphStyle('ReportTitle',fontName='YaHeiBold',fontSize=25,leading=37,textColor=colors.black,spaceAfter=18),
 'meta':ParagraphStyle('Meta',fontName='YaHei',fontSize=10,leading=16,textColor=colors.HexColor('#4b5563'),spaceAfter=10),
 'body':ParagraphStyle('Body',fontName='YaHei',fontSize=10.4,leading=17.5,wordWrap='CJK',spaceAfter=8,textColor=colors.HexColor('#17212b'),allowWidows=0,allowOrphans=0),
 'h1':ParagraphStyle('H1',fontName='YaHeiBold',fontSize=16,leading=23,spaceBefore=16,spaceAfter=10,keepWithNext=True,textColor=colors.black),
 'h2':ParagraphStyle('H2',fontName='YaHeiBold',fontSize=11.5,leading=18,spaceBefore=9,spaceAfter=6,keepWithNext=True,textColor=colors.black),
 'cell':ParagraphStyle('Cell',fontName='YaHei',fontSize=8.8,leading=13.5,wordWrap='CJK',textColor=colors.HexColor('#17212b')),
 'head':ParagraphStyle('CellHead',fontName='YaHeiBold',fontSize=8.8,leading=13.5,wordWrap='CJK',textColor=colors.white),
 'source':ParagraphStyle('Source',fontName='YaHei',fontSize=9.3,leading=15.2,wordWrap='CJK',spaceAfter=8,textColor=colors.HexColor('#17212b')),
 'toc':ParagraphStyle('TocEntry',fontName='YaHei',fontSize=10.5,leading=20,spaceBefore=4,textColor=colors.black),
}

def inline(text):
    text=html.escape(text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:f'<link href="{m.group(2)}" color="#1f4e68">{m.group(1)}</link>',text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'\[(S\d+)\]',r'<link href="#src\1" color="#1f4e68">[\1]</link>',text)
    return text

class ReportDoc(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=46,bottomMargin=44,
          title='AI 网站完整成本分析与降本方案',author='成本分析',subject='预算 任务成本 单位经济 降本优化',pageCompression=1)
        self.addPageTemplates(PageTemplate(id='main',frames=[Frame(M,44,CW,H-90,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.on_page))
    def on_page(self,canvas,doc):
        canvas.saveState()
        canvas.setFont('YaHei',8)
        canvas.setFillColor(colors.HexColor('#5b6570'))
        canvas.drawCentredString(W/2,23,f'第 {doc.page} 页')
        canvas.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name=='H1':
            text=f.getPlainText()
            if re.match(r'^\d+ ',text):
                key='sec'+text.split(' ')[0]
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text,key,level=0,closed=False)
                self.notify('TOCEntry',(0,text,self.page,key))

class CostBar(Flowable):
    def __init__(self): super().__init__(); self.width=CW; self.height=124
    def draw(self):
        c=self.canv
        values=[('模型与辅助',5521.84,'#153f5d'),('基础设施',2000,'#487b96'),('持续人力',30000,'#80a9bc'),('增长与内容',10000,'#c1d6df'),('行政',1000,'#e0e7eb')]
        total=sum(v for _,v,_ in values)
        c.setFillColor(colors.black);c.setFont('YaHeiBold',10)
        c.drawString(0,109,'1万月活情景的完整经营成本结构')
        x=0
        for name,v,col in values:
            bw=CW*v/total
            c.setFillColor(colors.HexColor(col));c.rect(x,71,bw,23,stroke=0,fill=1);x+=bw
        c.setFont('YaHei',9)
        for idx,(name,v,col) in enumerate(values):
            x=(idx%3)*166;y=49-(idx//3)*20
            c.setFillColor(colors.HexColor(col));c.rect(x,y,8,8,stroke=0,fill=1)
            c.setFillColor(colors.HexColor('#17212b'));c.drawString(x+13,y,f'{name} {v/total:.1%}')
        c.setFillColor(colors.HexColor('#5b6570'));c.setFont('YaHei',8)
        c.drawString(0,5,'规划演算  不含支付税费与风险缓冲  月经营成本约48,522元')

class FixedTOC(TableOfContents):
    def wrap(self,availWidth,availHeight):
        self.width=availWidth
        self.height=17*29
        return self.width,self.height
    def drawOn(self,canvas,x,y,_sW=0):
        canvas.saveState();canvas.translate(x,y)
        entries=self._lastEntries or [(0,'正在生成目录',1,'sec1')]
        for i,(level,title,page,key) in enumerate(entries):
            yy=self.height-(i+1)*29+8
            canvas.setFillColor(colors.black);canvas.setFont('YaHei',10.5)
            canvas.drawString(0,yy,title)
            canvas.drawRightString(self.width,yy,str(page))
            start=pdfmetrics.stringWidth(title,'YaHei',10.5)+9
            end=self.width-28
            if end>start:
                canvas.setFillColor(colors.HexColor('#99a6af'))
                for dx in range(int(start),int(end),5):canvas.circle(dx,yy+2,.45,stroke=0,fill=1)
            canvas.linkRect('',key,(0,yy-3,self.width,yy+15),relative=1,thickness=0)
        canvas.restoreState()

def table_widths(rows):
    n=len(rows[0]);headers=' '.join(rows[0])
    if n==5:return [CW*x for x in [.30,.12,.13,.12,.33]]
    if n==4:
        if '月活' in headers or '验证期' in headers or '验证型' in headers:return [CW*.43,CW*.19,CW*.19,CW*.19]
        if '优先级' in headers:return [CW*.09,CW*.28,CW*.19,CW*.44]
        if '规划工作量' in headers:return [CW*.27,CW*.19,CW*.25,CW*.29]
        return [CW*.26,CW*.25,CW*.25,CW*.24]
    if n==3:
        if '月模型费' in headers:return [CW*.54,CW*.22,CW*.24]
        if '计算' in headers:return [CW*.30,CW*.50,CW*.20]
        if '公开价格参照' in headers:return [CW*.25,CW*.24,CW*.51]
        if '成本项目' in headers:return [CW*.20,CW*.38,CW*.42]
        if '成本域' in headers:return [CW*.20,CW*.37,CW*.43]
        return [CW*.23,CW*.40,CW*.37]
    if n==2:return [CW*.28,CW*.72]
    return [CW/n]*n

def make_table(lines):
    rows=[[c.strip() for c in l.strip().strip('|').split('|')] for l in lines]
    aligns=rows[1];rows=rows[:1]+rows[2:]
    data=[]
    for ri,row in enumerate(rows):
        rr=[]
        for ci,t in enumerate(row):
            st=S['head' if ri==0 else 'cell'].clone(f'C{ri}-{ci}')
            if ri>0 and aligns[ci].rstrip().endswith(':'):st.alignment=TA_RIGHT
            rr.append(Paragraph(inline(t),st))
        data.append(rr)
    t=Table(data,colWidths=table_widths(rows),repeatRows=1,hAlign='LEFT',splitByRow=1)
    commands=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#234c64')),
      ('GRID',(0,0),(-1,-1),.45,colors.HexColor('#D9D9D9')),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),
      ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]
    for ri in range(1,len(rows)):
        if ri%2==0:commands.append(('BACKGROUND',(0,ri),(-1,ri),colors.HexColor('#f2f6f8')))
        if any(('合计' in cell or '小计' in cell or '月度资金预算' in cell or '完整经营成本' in cell) for cell in rows[ri]):
            commands.append(('BACKGROUND',(0,ri),(-1,ri),colors.HexColor('#e4edf2')))
    t.setStyle(TableStyle(commands))
    return t

text=(ROOT/'AI网站完整成本分析.md').read_text(encoding='utf-8')
assert '{{' not in text
lines=text.splitlines();story=[];i=0;body_started=False;meta_count=0;chapter=0;bar_done=False
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line.startswith('# '):
        story.append(Spacer(1,25));story.append(Paragraph(inline(line[2:]),S['title']));i+=1;continue
    if line.startswith('## '):
        if not body_started:
            story.append(PageBreak());story.append(Paragraph('阅读导航',S['h1']))
            story.append(Paragraph('先阅读第6节预算和第9至10节降本方案；第5节提供计算口径，第8节检验商业模式。目录页码与PDF书签均可用于定位。',S['body']))
            toc=FixedTOC();toc.levelStyles=[S['toc']]
            story.append(toc);story.append(PageBreak());body_started=True
        chapter=int(re.match(r'## (\d+)',line).group(1))
        if chapter==17:story.append(PageBreak())
        story.append(Paragraph(inline(line[3:]),S['h1']));i+=1;continue
    if line.startswith('### '):story.append(Paragraph(inline(line[4:]),S['h2']));i+=1;continue
    if line.startswith('|'):
        tl=[]
        while i<len(lines) and lines[i].strip().startswith('|'):tl.append(lines[i]);i+=1
        story.append(make_table(tl));story.append(Spacer(1,10))
        if chapter==6 and not bar_done:
            story.append(CostBar());story.append(Spacer(1,4));bar_done=True
        continue
    para=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|')):para.append(lines[i].strip());i+=1
    raw=''.join(para)
    if not body_started and meta_count<2:
        st=S['meta'];meta_count+=1
    else:st=S['source'] if chapter==17 else S['body']
    formatted=inline(raw)
    if chapter==17:
        sm=re.match(r'\[(S\d+)\]',raw)
        if sm:formatted=f'<a name="src{sm.group(1)}"/>'+formatted
    story.append(Paragraph(formatted,st))

path=OUT/'AI网站完整成本分析与降本方案.pdf'
doc=ReportDoc(path)
doc.multiBuild(story)
reader=PdfReader(path)
page_text=[p.extract_text() or '' for p in reader.pages]
(ROOT/'qa').mkdir(exist_ok=True)
(ROOT/'qa'/'page_text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{x}' for i,x in enumerate(page_text)),encoding='utf-8')
print(json.dumps({'pdf':str(path),'pages':len(reader.pages),'chars':sum(map(len,page_text)), 'bytes':path.stat().st_size},ensure_ascii=True))
assert len(reader.pages)>=12
assert all(len(x.strip())>30 for x in page_text)
assert '50,026' in ''.join(page_text)
assert '34,631' in ''.join(page_text)
assert not re.search(r'\{\{|\ufffd', ''.join(page_text))
