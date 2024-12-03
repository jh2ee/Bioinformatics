#!/usr/bin/env python

from optparse import OptionParser
import os
import numpy as np

class TM_result:
    def __init__(self):
        self.tm = 0.0
        self.rmsd = 0.0

def TM_align_rmsd(pdb_fn, ref_fn, l_seq=0):
    t = []
    r = [[], [], []]
    tm = TM_result()
    cmd = []
    cmd.append('~/biodata/biolip/TMalign')
    cmd.append('%s' % pdb_fn)
    cmd.append('%s' % ref_fn)
    if l_seq != 0:
        cmd.append('-L %d' % l_seq)
    cmd.append('2> /dev/null')
    cmd = (' ').join(cmd)
    lines = os.popen(cmd).readlines()
    if len(lines) == 0:
        print(cmd)
        return None
    j = None
    for i, line in enumerate(lines):
        if line.startswith('(":" denotes'):
            i_aln = i + 1
            break
        elif 'Rotation matrix' in line:
            j = i + 2
        elif 'TM-score=' in line:
            tm.tm = float(line.strip().split(',')[2].split('=')[1])
            tm.rmsd = float(line.strip().split(',')[1].split('=')[1])
    return tm.rmsd

def runDockQ(pdb_fn, ref_fn, prnout=False):
    iR = 9999
    lR = 9999
    fnat = 0
    cmd = []
    cmd.append('~/pros/DockQ/DockQ.py -capri_peptide')
    cmd.append('%s' % pdb_fn)
    cmd.append('%s' % ref_fn)
    cmd.append('2> /dev/null')
    cmd = (' ').join(cmd)
    if (prnout):
        print(cmd)
        os.system(cmd)
    lines = os.popen(cmd).readlines()
    if len(lines) == 0:
        print(cmd)
        return (lR, iR, fnat)
    for i, line in enumerate(lines):
        if line.startswith('iRMS'):
            iR = float(line.split()[1])
        elif line.startswith('LRMS'):
            lR = float(line.split()[1])
        elif line.startswith('Fnat'):
            fnat = float(line.split()[1])
    return (lR, iR, fnat)

def noprn(text):
    return None

usage = "USAGE: python calcrmsds4bench.py --fn listfilename --bu (b or u) --db (p or d) \n"
parser = OptionParser(usage=usage)
parser.add_option("--fn",help="File name to read", dest="fn")
parser.add_option("--bu",help="whether target is bound or unbound", default = 'u', dest="bu")
parser.add_option("--db",help="use peppro list?", default = 'p', dest="db")
parser.add_option("--na",help="nth run", default = 1, dest="na")
(options, args) = parser.parse_args()
boru = 1 #0/1 if using bound/unbound pdb
prncmds = 1
peppro = 1 #1 if peppro benchmark peptide chain id ahead of protein (reverse in gpd)
if (prncmds):
    prnfnc = print
else:
    prnfnc = noprn
if (options.bu == 'b'):
    boru = 0
if (options.db != 'p'):
    peppro = 0
mdirna = ""
#if (options.na == '1'):
#    mdirna = ""
#else:
#    mdirna = options.na
    
try:
    listfile = open(options.fn,'r')
except IOError:
    print("list/output file IO error")
    quit()
cwd = os.getcwd()
cnt = 0
while True:
    listline = listfile.readline()
    if not listline:
        break
    if "2P1K" in listline: #2P1K is replaced (with 3E2B) in PDB database
        continue
    #if "1OU8" in listline: #special case for 1OU8 since 1OU8_B in biolip and 1OU8 A==B
    #    listline = "1OU8_A:C 3SEM_A:C 0.539 GAANDENY PPPVPR 26.01 25.47"
    fd = listline.split()
    protbase = fd[boru].split('_')[0]
    #protchain = fd[boru].split('_')[1][0]
    #protfn = protbase+protchain+".pdb"
    #fafn = fd[boru].split('_')[0]+".fa"

    if (peppro):
        boundprotbase = fd[0].split('_')[0]
        boundpepchain = fd[0].split('_')[1][0]
        boundprotchain = fd[0].split(':')[1][0]   
    else:
        boundprotbase = fd[0].split('_')[0]
        boundprotchain = fd[0].split('_')[1][0]
        boundpepchain = fd[0].split(':')[1][0]
    #nativet = boundprotbase+boundprotchain+boundpepchain+".pdb"
    native = boundprotbase+"AB.pdb"

    #qseq = fd[3]
    #cmd = "echo "+qseq+" > "+fafn
    #print(cmd)
    #os.system(cmd)
    #print(fasfn, code)
    cnt += 1
    #if (cnt > 5):
    #    break
    if not (os.path.isfile(boundprotbase+".pdb")):
        cmd = "wget https://files.rcsb.org/download/"+boundprotbase+".pdb &> /dev/null"
        prnfnc(cmd)
        os.system(cmd)
    #cmd = "python ~/pros/pdb-tools/pdbtools/pdb_selchain.py -"+boundprotchain+" "+boundprotbase+".pdb"+" > "+protfn
    #print(cmd)
    #os.system(cmd)
    cmd = "python ~/pros/pdb-tools/pdbtools/pdb_selchain.py -"+boundprotchain+" "+boundprotbase+".pdb"+" > "\
          +boundprotbase+boundprotchain+".pdb"
    prnfnc(cmd)
    os.system(cmd)
    nAfile = boundprotbase+boundprotchain+".pdb"
    if (boundprotchain != 'A'):
        cmd = "python ~/pros/pdb-tools/pdbtools/pdb_rplchain.py -"+boundprotchain+":A "+boundprotbase+boundprotchain+".pdb > "\
              +boundprotbase+boundprotchain+"_A.pdb"
        prnfnc(cmd)
        os.system(cmd)
        nAfile = boundprotbase+boundprotchain+"_A.pdb"
    cmd = "python ~/pros/pdb-tools/pdbtools/pdb_selchain.py -"+boundpepchain+" "+boundprotbase+".pdb"+" > "\
          +boundprotbase+boundpepchain+".pdb"
    prnfnc(cmd)
    os.system(cmd)
    nBfile = boundprotbase+boundpepchain+".pdb"
    if (boundpepchain != 'B'):
        cmd = "python ~/pros/pdb-tools/pdbtools/pdb_rplchain.py -"+boundpepchain+":B "+boundprotbase+boundpepchain+".pdb > "\
              +boundprotbase+boundpepchain+"_B.pdb"
        prnfnc(cmd)
        os.system(cmd)
        nBfile = boundprotbase+boundpepchain+"_B.pdb"
    cmd = "python ~/pros/pdb-tools/pdbtools/pdb_merge.py "+nAfile+" "+nBfile+" > natmp.pdb"
    prnfnc(cmd)
    os.system(cmd)
    cmd = "python ~/pros/pdb-tools/pdbtools/pdb_tidy.py natmp.pdb > " + native
    prnfnc(cmd)
    os.system(cmd)

    minlrmsd = 9999
    minirmsd = 9999
    maxfnat = 0
    for mindex in range (1, 11):
        modelfile = protbase+mdirna+"/model/model_"+str(mindex)+".pdb"
        mAfile = protbase+mdirna+"/model/model_"+str(mindex)+"A.pdb"
        mBfile = protbase+mdirna+"/model/model_"+str(mindex)+"B.pdb"
        if (os.path.isfile(modelfile)):
            cmd = "python ~/pros/pdb-tools/pdbtools/pdb_selchain.py -A "+modelfile+" > "+mAfile
            prnfnc(cmd)
            os.system(cmd)
            cmd = "~/pros/DockQ/scripts/fix_numbering.pl "+mAfile+" "+nAfile+" > /dev/null"
            prnfnc(cmd)
            os.system(cmd)
            cmd = "python ~/pros/pdb-tools/pdbtools/pdb_selchain.py -B "+modelfile+" > tmppdb"
            prnfnc(cmd)
            os.system(cmd)
            cmd = "python ~/pros/pdb-tools/pdbtools/pdb_keepcoord.py tmppdb > "+mBfile
            prnfnc(cmd)
            os.system(cmd)
            cmd = "~/pros/DockQ/scripts/fix_numbering.pl "+mBfile+" "+nBfile+" > /dev/null"
            prnfnc(cmd)
            os.system(cmd)
            cmd = "python ~/pros/pdb-tools/pdbtools/pdb_merge.py "+mAfile+".fixed "+mBfile+".fixed > modeltmp.pdb"
            prnfnc(cmd)
            os.system(cmd)
            cmd = "python ~/pros/pdb-tools/pdbtools/pdb_tidy.py modeltmp.pdb > " +modelfile+".AB.fixed"
            prnfnc(cmd)
            os.system(cmd)
            
            lr, ir, fn = runDockQ(modelfile+".AB.fixed", native)
            if minlrmsd > lr:
                minlrmsd = lr
            if minirmsd > ir:
                minirmsd = ir
            if maxfnat < fn:
                maxfnat = fn

    print(boundprotbase, minlrmsd, minirmsd, maxfnat)
    #break
    

    
