latex bare_conf
bibtex bare_conf
latex bare_conf
latex bare_conf
dvips -Ppdf -t letter -G0 bare_conf
ps2pdf14 -dPDFSETTINGS#/prepress -dEmbedAllFonts#true -dEncodeGrayImages#true -dAutoFilterGrayImages#false -dGrayImageFilter#/FlateEncode -dEncodeMonoImages#true -dAutoFilterMonoImages#false -dMonoImageFilter#/FlateEncode -dEncodeColorImages#true -dAutoFilterColorImages#false -dColorImageFilter#/FlateEncode bare_conf.ps bare_conf.pdf
