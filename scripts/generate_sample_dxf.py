"""Generate a sample complex framed DXF using ezdxf for demo/testing."""
import ezdxf
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--out', '-o', default='examples/sample_frame.dxf')
args = parser.parse_args()

def make_frame(doc):
    msp = doc.modelspace()
    # create a grid of beams and columns with varying heights and a diagonal brace
    spacing = [0, 5, 10]
    for i,x in enumerate(spacing):
        for j,y in enumerate(spacing):
            # vertical column
            z0 = 0
            z1 = 3 + i # vary heights
            msp.add_line((x,y,z0), (x,y,z1), dxfattribs={'layer':'COLUMNS'})
    # beams between columns
    for i in range(len(spacing)-1):
        x1 = spacing[i]
        x2 = spacing[i+1]
        msp.add_line((x1,0,3), (x2,0,3), dxfattribs={'layer':'BEAMS'})
        msp.add_line((x1,5,3), (x2,5,3), dxfattribs={'layer':'BEAMS'})
    # diagonal brace
    msp.add_line((0,0,3), (10,10,0), dxfattribs={'layer':'BRACES'})

if __name__ == '__main__':
    doc = ezdxf.new(dxfversion='R2010')
    make_frame(doc)
    out = args.out
    doc.saveas(out)
    print('Wrote sample DXF to', out)
