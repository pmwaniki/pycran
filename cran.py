#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 12:40:58 2017

@author: pmwaniki
"""

import argparse
from subprocess import Popen
import tempfile




parser=argparse.ArgumentParser(description="Manage system R packages.")
parser.add_argument("--version","-V",action='version',version='Version 1.0 (alpha)')

subparser=parser.add_subparsers(dest="command")


parser_install=subparser.add_parser("install",help="Install packages")
parser_install.add_argument("packages",nargs="+",help="packages to be installed")
parser_install.add_argument("--lib",help="library path")
parser_install.add_argument("--versions",nargs="+")

parser_remove=subparser.add_parser("remove",help="Remove packages")
parser_remove.add_argument("packages",nargs=1,help="package to be removed")
parser_remove.add_argument("--lib",help="library path")

parser_available=subparser.add_parser("available",help="Check version of installed package")
parser_available.add_argument("packages",help="packages",nargs="+")

parser_query=subparser.add_parser("query",help="Check available package versions from cran")
parser_query.add_argument("packages",nargs="+",help="packages to query from cran")
parser_query.add_argument("--number",nargs="?",default=5,type=int,help="Number of entries to display")

#args=parser.parse_args("install car reshape2 --versions 1.0 0.3".split())
#args=parser.parse_args("install car reshape2 --lib='/usr/local/bin'".split())
#args=parser.parse_args("remove car".split())

args=parser.parse_args()
#parser.format_help()


install_versions_str=\
"""
ins<-installed.packages()
ins<-as.data.frame(ins,row.names=1:nrow(ins),stringsAsFactors = F)
if(!"versions" %in% ins$Package) install.packages("versions",repos='http://cran.rstudio.com')
"""

install_str= \
"""
ins<-installed.packages()
ins<-as.data.frame(ins,row.names=1:nrow(ins),stringsAsFactors = F)
if(!"versions" %in% ins$Package) install.packages("versions",repos='http://cran.rstudio.com')
library(versions)
{installer}({packs})
"""

remove_str=\
"""
ins<-installed.packages()
ins<-as.data.frame(ins,row.names=1:nrow(ins),stringsAsFactors = F)

ins2<-ins[,c('Package','Version','LibPath')]
ins2<-ins2[order(ins2$Package),]
row.names(ins2)<-NULL
ins2<-ins2[ins2$Package %in% c({packs}),]
row.names(ins2)<-NULL
paths<-ins2$LibPath




remove.packages({packs},lib = paths[{row}])

"""

query_str=\
"""
ins<-installed.packages()
ins<-as.data.frame(ins,row.names=1:nrow(ins))
if(!"versions" %in% ins$Package) install.packages("versions",repos='http://cran.rstudio.com')
library(versions)
av<-available.versions(c({packs}))
sapply(av,function(x) head(x[,c("version","date")],{n}),simplify=F)
"""

available_str=\
"""
ins<-installed.packages()
ins<-as.data.frame(ins,row.names=1:nrow(ins))
ins2<-ins[,c('Package','Version','LibPath')]
ins2<-ins2[order(ins2$Package),]
row.names(ins2)<-NULL
ins2<-ins2[ins2$Package %in% c({packs}),]
row.names(ins2)<-NULL
ins2
"""



def run(run_string):
    fp = tempfile.NamedTemporaryFile(mode="w",suffix=".R")
    fp.write(run_string)
    fp.flush()
    process=Popen("R --vanilla -q --slave  <"+ fp.name,
                  universal_newlines=True,shell=True)
    process.wait()
    fp.close()

if(args.command=="install"):
    packages=args.packages
    versions=args.versions
    if versions and len(versions) != len(packages):
        raise Exception("differing number of packages and versions")
    packs="pkgs=c("+",".join("'"+p+"'" for p in packages) + ")"
        
    if args.lib :
        packs=packs + ",lib='" + args.lib + "'"
                
    if versions:
        packs=packs + ",versions=c("+ \
        ",".join("'"+v+"'" for v in versions) +")"
        run_string=install_str.format(**{'installer':'install.versions','packs':packs})
        
    else:
        packs=packs + ",repos='http://cran.rstudio.com'"        
        run_string=install_str.format(**{'installer':'install.packages','packs':packs})
    run(run_string)

if(args.command=="remove"):
    packs=",".join("'"+p+"'" for p in args.packages)
    run(available_str.format(**{'packs':packs}))
    row=input("select package to remove :")
    run_string=remove_str.format(**{'packs':packs,'row':row})
    run(run_string)
    
    
    
if(args.command=="query"):
    
    packs=",".join("'"+p+"'" for p in args.packages)   
    run_string=query_str.format(**{'packs':packs,'n':str(args.number)})
    run(run_string)
    
if(args.command=="available"):
    packs=",".join("'"+p+"'" for p in args.packages)   
    run_string=available_str.format(**{'packs':packs})
    run(run_string)        

#print(run_string)


