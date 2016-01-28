size(12cm,10cm,IgnoreAspect);

import graph;
import palette;
import cooltowarm;

string filename = getstring("filename","testout/meansuccess0.dat");

file in1=input(filename).line().csv();
real[][] f=in1.dimension(0,0);

int t0 = getint("t0");

write(f.length);
write(f[0].length);

pen[] Palette;

if(min(f) < 0 && max(f) > 0)
  Palette=cooltowarm(min(f),0,max(f));
else {
  if(min(f) < 0)
    Palette = cooltowhite;
  if(max(f) > 0)
    Palette = whitetowarm;
}
//Pallette = BWRainbow();

//image(v, (0,0), (1,1), Palette);

real maxsavings = 0.35;

picture bar;
bounds range=image(f,(t0,1.0 - maxsavings),(130,1),Palette);

// Make the colour bar go from 0 to 1:
range.min = 0;
range.max = 1;

palette(bar,"probabilty of success",range,(0,0),(0.5cm,6cm),Right,Palette,
        PaletteTicks("$%+#.1f$"));
add(bar.fit(),point(E),30E);


xaxis("time",BottomTop,RightTicks,above=true);
yaxis("$p_d/p(t_0)$",LeftRight,LeftTicks,above=true);
