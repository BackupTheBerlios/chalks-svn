""" Run me from the src/ dir. More instructions on the bottom of this script
"""

hdr = """<?xml version="1.0" encoding="UTF-8"?>
<dia:diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">
  <dia:diagramdata>
    <dia:attribute name="background">
      <dia:color val="#ffffff"/>
    </dia:attribute>
    <dia:attribute name="pagebreak">
      <dia:color val="#000099"/>
    </dia:attribute>
    <dia:attribute name="paper">
      <dia:composite type="paper">
        <dia:attribute name="name">
          <dia:string>#A4#</dia:string>
        </dia:attribute>
        <dia:attribute name="tmargin">
          <dia:real val="2.8222000598907471"/>
        </dia:attribute>
        <dia:attribute name="bmargin">
          <dia:real val="2.8222000598907471"/>
        </dia:attribute>
        <dia:attribute name="lmargin">
          <dia:real val="2.8222000598907471"/>
        </dia:attribute>
        <dia:attribute name="rmargin">
          <dia:real val="2.8222000598907471"/>
        </dia:attribute>
        <dia:attribute name="is_portrait">
          <dia:boolean val="true"/>
        </dia:attribute>
        <dia:attribute name="scaling">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="fitto">
          <dia:boolean val="false"/>
        </dia:attribute>
      </dia:composite>
    </dia:attribute>
    <dia:attribute name="grid">
      <dia:composite type="grid">
        <dia:attribute name="width_x">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="width_y">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="visible_x">
          <dia:int val="1"/>
        </dia:attribute>
        <dia:attribute name="visible_y">
          <dia:int val="1"/>
        </dia:attribute>
        <dia:composite type="color"/>
      </dia:composite>
    </dia:attribute>
    <dia:attribute name="color">
      <dia:color val="#d8e5e5"/>
    </dia:attribute>
    <dia:attribute name="guides">
      <dia:composite type="guides">
        <dia:attribute name="hguides"/>
        <dia:attribute name="vguides"/>
      </dia:composite>
    </dia:attribute>
  </dia:diagramdata>
  <dia:layer name="Background" visible="true">

"""

kls_templ = """
    <dia:object type="UML - Class" version="0" id="O%d">
      <dia:attribute name="obj_pos">
        <dia:point val="6.4,9.45"/>
      </dia:attribute>
      <dia:attribute name="obj_bb">
        <dia:rectangle val="6.35,9.4;9.2,11.7"/>
      </dia:attribute>
      <dia:attribute name="elem_corner">
        <dia:point val="6.4,9.45"/>
      </dia:attribute>
      <dia:attribute name="elem_width">
        <dia:real val="2.75"/>
      </dia:attribute>
      <dia:attribute name="elem_height">
        <dia:real val="2.1999999999999997"/>
      </dia:attribute>
      <dia:attribute name="name">
        <dia:string>#%s#</dia:string>
      </dia:attribute>
      <dia:attribute name="stereotype">
        <dia:string>##</dia:string>
      </dia:attribute>
      <dia:attribute name="comment">
        <dia:string>##</dia:string>
      </dia:attribute>
      <dia:attribute name="abstract">
        <dia:boolean val="false"/>
      </dia:attribute>
      <dia:attribute name="suppress_attributes">
        <dia:boolean val="false"/>
      </dia:attribute>
      <dia:attribute name="suppress_operations">
        <dia:boolean val="false"/>
      </dia:attribute>
      <dia:attribute name="visible_attributes">
        <dia:boolean val="true"/>
      </dia:attribute>
      <dia:attribute name="visible_operations">
        <dia:boolean val="true"/>
      </dia:attribute>
      <dia:attribute name="visible_comments">
        <dia:boolean val="false"/>
      </dia:attribute>
      <dia:attribute name="wrap_operations">
        <dia:boolean val="true"/>
      </dia:attribute>
      <dia:attribute name="wrap_after_char">
        <dia:int val="40"/>
      </dia:attribute>
      <dia:attribute name="line_color">
        <dia:color val="#000000"/>
      </dia:attribute>
      <dia:attribute name="fill_color">
        <dia:color val="#ffffff"/>
      </dia:attribute>
      <dia:attribute name="text_color">
        <dia:color val="#000000"/>
      </dia:attribute>
      <dia:attribute name="normal_font">
        <dia:font family="monospace" style="0" name="Courier"/>
      </dia:attribute>
      <dia:attribute name="abstract_font">
        <dia:font family="monospace" style="88" name="Courier"/>
      </dia:attribute>
      <dia:attribute name="polymorphic_font">
        <dia:font family="monospace" style="8" name="Courier"/>
      </dia:attribute>
      <dia:attribute name="classname_font">
        <dia:font family="sans" style="80" name="Helvetica"/>
      </dia:attribute>
      <dia:attribute name="abstract_classname_font">
        <dia:font family="sans" style="88" name="Helvetica"/>
      </dia:attribute>
      <dia:attribute name="comment_font">
        <dia:font family="sans" style="8" name="Helvetica"/>
      </dia:attribute>
      <dia:attribute name="font_height">
        <dia:real val="0.80000000000000004"/>
      </dia:attribute>
      <dia:attribute name="polymorphic_font_height">
        <dia:real val="0.80000000000000004"/>
      </dia:attribute>
      <dia:attribute name="abstract_font_height">
        <dia:real val="0.80000000000000004"/>
      </dia:attribute>
      <dia:attribute name="classname_font_height">
        <dia:real val="1"/>
      </dia:attribute>
      <dia:attribute name="abstract_classname_font_height">
        <dia:real val="1"/>
      </dia:attribute>
      <dia:attribute name="comment_font_height">
        <dia:real val="1"/>
      </dia:attribute>
      <dia:attribute name="attributes"/>
      <dia:attribute name="operations">
      %s
      </dia:attribute>      
      <dia:attribute name="template">
        <dia:boolean val="false"/>
      </dia:attribute>
      <dia:attribute name="templates"/>
    </dia:object>
"""

ftr = """
  </dia:layer>
</dia:diagram>
"""

def genkls(kls, lst):
    global kls_count
    for klas in lst:
        mbrs = getmembers(getattr(kls, klas))
        oprs = ""
        for nm, obj in mbrs:
            if nm[0] == '_': continue
            parms_templ = \
"""
            <dia:composite type="umlparameter">
              <dia:attribute name="name">
                <dia:string>#%s#</dia:string>
              </dia:attribute>
              <dia:attribute name="type">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="value">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="comment">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="kind">
                <dia:enum val="0"/>
              </dia:attribute>
            </dia:composite>
"""
            parms = " "
            try:
                prms = getargspec(obj)
            except:
                prms = []
            else:                
                prms = prms[0][1:]
            for prm in prms:
                parms += parms_templ % prm
            oprs += \
    """
            <dia:composite type="umloperation">
              <dia:attribute name="name">
                <dia:string>#%s#</dia:string>
              </dia:attribute>
              <dia:attribute name="stereotype">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="type">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="visibility">
                <dia:enum val="0"/>
              </dia:attribute>
              <dia:attribute name="comment">
                <dia:string>##</dia:string>
              </dia:attribute>
              <dia:attribute name="abstract">
                <dia:boolean val="false"/>
              </dia:attribute>
              <dia:attribute name="inheritance_type">
                <dia:enum val="2"/>
              </dia:attribute>
              <dia:attribute name="query">
                <dia:boolean val="false"/>
              </dia:attribute>
              <dia:attribute name="class_scope">
                <dia:boolean val="false"/>
              </dia:attribute>
              <dia:attribute name="parameters">
              %s
              </dia:attribute>
            </dia:composite>
    """ % (nm, parms)

        print kls_templ % (kls_count,klas,oprs)
        kls_count += 1        
        
from inspect import *

try: ### Add your imports here
    import Chalks
    import ConcurrentEditable
except:
    print "Run from src/ dir !"
    import sys
    sys.exit()

print hdr

kls_count = 0
### add your modules / classes here :
genkls(Chalks, ['Chalks','ChalksNode','ChalksAvatar', 'ChalksServerMonitor'])
genkls(ConcurrentEditable, ['ConcurrentEditable','ConcurrentEditableServer','ConcurrentEditableClient', 'ConcurrentEditableNode'])
print ftr

"""
for each module, add a genkls() call. First parameter is a module object, 2nd parm is a list of classes to extract. A DIA compatible XML will be printed.
"""
