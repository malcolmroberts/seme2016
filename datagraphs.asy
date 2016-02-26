import graph;
import utils;

//asy datagraphs -u "xlabel=\"\$\\bm{u}\cdot\\bm{B}/uB$\"" -u "doyticks=false" -u "ylabel=\"\"" -u "legendlist=\"a,b\""

// -u "ymax=2"

texpreamble("\usepackage{bm}");

size(300,200,IgnoreAspect);

scale(Linear,Linear);

bool dolegend=false;

real ymax = 0.0;

string filenames=getstring("filenames");
string filename;
string legendlist="";
int n=-1;
bool flag=true;
int lastpos;

bool doxticks=true;
bool doyticks=true;
string xlabel="Day";
string ylabel="Price";

usersetting();
bool myleg=((legendlist == "") ? false: true);
string[] legends=set_legends(legendlist);

write(legends);

while(flag) {
  ++n;
  int pos=find(filenames,",",lastpos);
  if(lastpos == -1) {
    filename="";
    flag=false;
  }
  
  if(flag) {
    filename=substr(filenames,lastpos,pos-lastpos);
    write("filename: " + filename);
    if(myleg) write(legends[n]);
    
    lastpos=pos > 0 ? pos + 1 : -1;
    
    
    file fin=input(filename).line();
    real[][] a=fin.dimension(0,0);
    a=transpose(a);
    real[] x=a[0];
    real[] y=a[1];
    x -= 130;
    pen p=Pen(n);
    if(n == 1) p += dashed;
    if(n == 2) p = darkgreen + Dotted;
    if(ymax > 0)
      draw(graph(x,y,y < ymax), p,myleg ? legends[n] : texify(filename));
    else
      draw(graph(x,y), p,myleg ? texify(legends[n]) : texify(filename));
  }
}

if(doxticks)
  xaxis(xlabel,BottomTop,LeftTicks);
else
  xaxis(xlabel);
if(doyticks)
  yaxis(ylabel,LeftRight,RightTicks);
else
  yaxis(ylabel,LeftRight);
if(dolegend) attach(legend(),point(plain.E),20plain.E);
