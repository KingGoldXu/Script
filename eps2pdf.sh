#!/bin/bash
epstool --copy --bbox $1 my_epstopdf_temp.eps
epstopdf --hires --outfile=$2 my_epstopdf_temp.eps
rm my_epstopdf_temp.eps
