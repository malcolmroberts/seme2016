size(12cm,12cm);

import graph;
import palette;
import cooltowarm;

string filename = getstring("filename","testout/meansuccess0.dat");

file in1=input(filename).line().csv();
real[][] f=in1.dimension(0,0);

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

picture bar;
bounds range=image(f,(0,0),(1,1),Palette);
palette(bar,"$A$",range,(0,0),(0.5cm,8cm),Right,Palette,
        PaletteTicks("$%+#.1f$"));
add(bar.fit(),point(E),30E);

