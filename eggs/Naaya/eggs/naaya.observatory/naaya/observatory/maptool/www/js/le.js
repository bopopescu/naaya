/* http://www.2crossmedia.com
   living elements for jQuery
   Written by 2crossmedia (info{at}2crossmedia.com) april 2010.
*/

eval(function (p, a, c, k, e, r) {
    e = function (c) {
        return (c < a ? '' : e(parseInt(c / a))) + ((c = c % a) > 35 ? String.fromCharCode(c + 29) : c.toString(36))
    };
    if (!''.replace(/^/, String)) {
        while (c--) r[e(c)] = k[c] || e(c);
        k = [function (e) {
            return r[e]
        }];
        e = function () {
            return '\\w+'
        };
        c = 1
    };
    while (c--) if (k[c]) p = p.replace(new RegExp('\\b' + e(c) + '\\b', 'g'), k[c]);
    return p
}('1c.D=8(a){3(C.1d){1d.D(a)}n{}};(8($){$.1w.1x=8(g,h){p j={E:\'#1y\',z:\'1z\',S:0,1e:1f,1g:1f,I:9,T:\'L\',U:\'M\',N:9,V:1h,W:q,w:1,J:0,X:\'Y\',r:0,s:0,t:9,u:9,1i:q,F:1A,G:9,Z:9,10:1h};3(h)$.1B(j,h);j.11=(j.w+j.J)/2;p k;p l=(H.1j=="12 1k 1l"&&1m(H.O)==4&&H.O.13("1n 5.5")!=-1);p m=(H.1j=="12 1k 1l"&&1m(H.O)==4&&H.O.13("1n 6.0")!=-1);3((l||m)&&j.1e)1o o;o.1p(8(){p d={14:$(o).1C(),15:$(o).1D(),r:j.r,s:j.s};3(j.t===9){3(j.X==\'Y\')d.t=d.14;n d.t=d.r}n d.t=j.t;3(j.u===9)3(j.X==\'Y\')d.u=d.s;n d.u=d.15;n d.u=j.u;d.16=(d.r+d.t)/2;d.17=(d.s+d.u)/2;3($(o).7(\'P\')==\'1E\')$(o).7(\'P\',\'1F\');$(o).18().7(\'P\',\'1q\');p e=$(o).1r().1G().7(\'P\',\'1q\').7(\'E\',\'1s(\'+g+\')\').7(\'1H\',d.14).7(\'1I\',d.15).1J(\'1K\',\'\').1t(o);p f=e.1r().7(\'E\',j.E).7(\'A\',d.r+\'v \'+d.s+\'v\').1t(o);3(j.N!==9)f.7(\'x\',j.N);n f.7(\'x\',j.w);3(l||m){$.1p([e],8(i,a){p b=a.7(\'E-1u\');3(b.13(".1v")!=-1){p c=b.19(\'1s("\')[1].19(\'")\')[0];a.7(\'E-1u\',\'1L\');a.1M(0).1N.1O="1P:1Q.12.1R(1S=\'1T/1U-1V.1v\',1W=\'1X\')"}})}3(j.I==9||j.1g){Q(f,j,d)}3(j.I!=9){$(o).18(j.I).L(8(){3(j.T==\'L\')Q(f,j,d);n 3(j.U==\'L\')1a(f,j,d)});$(o).18(j.I).M(8(){3(j.T==\'M\')Q(f,j,d);n 3(j.U==\'M\')1a(f,j,d)})}});1o o;8 Q(a,b,c){3(b.N!==9){k=C.K(8(){$.D(b.w);a.y(q).B({\'x\':b.w},b.V,b.z)},b.S)}k=C.K(8(){1b(a,b,c)},b.V+b.S)}8 1a(a,b,c){C.1Y(k);3(b.W){3(b.G!=9)a.y(q).B({\'x\':b.w},b.G,b.z);n a.y(q).7(\'x\',b.w)}n{3(b.G!=9){a.y(q).B({A:\'(\'+c.r+\'v \'+c.s+\'v)\'},b.G,b.z)}}3(b.Z!=9){k=C.K(8(){a.y(q).B({\'x\':b.Z},b.10,b.z);C.K(8(){a.y(q).7(\'A\',c.r+\'v \'+c.s+\'v\')},b.10)},b.G)}}8 1b(a,b,c){$.D($(a).7(\'A\'));3(b.W){3((b.w<=b.J&&R(a.7(\'x\'))>b.11)||(b.w>=b.J&&R(a.7(\'x\'))<b.11)){a.y(q).B({\'x\':b.w},b.F,b.z)}n{a.y(q).B({\'x\':b.J},b.F,b.z)}}n{p d;p e;3($(a).7(\'A\')==\'0% 0%\'){d=0;e=0}n{p f=$(a).7(\'A\').19(\'v\');d=R(f[0]);e=R(f[1])}3((c.t>=c.r&&d>c.16)||(c.t<=c.r&&d<c.16)||(c.u>=c.s&&e>c.17)||(c.u<=c.s&&e<c.17)){$.D(c.r+\' \'+c.s+\' \'+c.t+\' \'+c.u);$(a).y(q).B({A:\'(\'+c.r+\'v \'+c.s+\'v)\'},b.F,b.z)}n{$(a).y(q).B({A:\'(\'+c.t+\'v \'+c.u+\'v)\'},b.F,b.z)}}3(b.1i)k=C.K(8(){1b(a,b,c)},b.F)}$.D($(1Z).7(\'A\'))}})(1c);', 62, 124, '|||if||||css|function|null||||||||||||||else|this|var|true|mainAnimationStartBackgroundPositionX|mainAnimationStartBackgroundPositionY|mainAnimationEndBackgroundPositionX|mainAnimationEndBackgroundPositionY|px|mainAnimationStartOpacity|opacity|stop|easing|backgroundPosition|animate|window|log|background|mainAnimationDuration|mainAnimationSoftEndDuration|navigator|triggerElementSelector|mainAnimationEndOpacity|setTimeout|focus|blur|preAnimationStartOpacity|appVersion|position|startAnimation|parseFloat|delay|triggerElementStartEvent|triggerElementStopEvent|preAnimationDuration|mainAnimationFade|mainAnimationScrollDirection|horizontal|postAnimationEndOpacity|postAnimationDuration|averageOpacity|Microsoft|indexOf|elementWidth|elementHeight|averageBackgroundPositionX|averageBackgroundPositionY|children|split|endAnimation|_animateMask|jQuery|console|disableIE6|false|startOnLoad|500|mainAnimationContinous|appName|Internet|Explorer|parseInt|MSIE|return|each|absolute|clone|url|prependTo|image|png|fn|livingElements|33CCFF|swing|1000|extend|outerWidth|outerHeight|static|relative|empty|width|height|attr|class|none|get|runtimeStyle|filter|progid|DXImageTransform|AlphaImageLoader|src|images|input|mask|sizingMethod|scale|clearTimeout|elem'.split('|'), 0, {}))
