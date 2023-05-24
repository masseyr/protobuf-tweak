#!/usr/bin/python3
import os,shutil,glob,sys,argparse
import tarfile
from subprocess import Popen, PIPE


def selectCompilerFlags(arch):
    compilerFlags = {}
    if(arch =='gfortran-openmp'):
        compilerFlags['gfortran-openmp']={}
        compilerFlags['gfortran-openmp']['Compiler']='gfortran'
        fullGfortranPath = which('gfortran')
        if(fullGfortranPath ==''): sys.exit("No gfortran found in path.")

        gccBinPath = os.path.split(fullGfortranPath)[0]
        gccPath = os.path.split(gccBinPath)[0]

        # bit to check what gcc version is available, if not > 6. Problem. exit.
        p = Popen(['gfortran','-dumpversion'], stdout = PIPE, stderr = PIPE) 
        p.wait()
        so,se = p.communicate() 
        if ( int(so.decode("utf-8").split('.')[0]) < 6 ):
            sys.exit("F2008 required. gcc >= 6")
        compilerFlags['gfortran-openmp']['FCFLAGS1']="-O3 -fimplicit-none -ffree-form -fno-second-underscore -frecord-marker=4 -funroll-loops -fopenmp -Wall -Wconversion -mieee-fp -fbounds-check -std=f2008 -fPIC"
        compilerFlags['gfortran-openmp']['FCFLAGS2']=""   
        compilerFlags['gfortran-openmp']['LDFLAGS']="-Wall -g -shared -lnetcdf -lnetcdff -lhdf5 "
        compilerFlags['gfortran-openmp']['F2PY_COMPILER']="gnu95"
   
    elif(arch == 'ifort-openmp'):
        compilerFlags['ifort-openmp']={}
        compilerFlags['ifort-openmp']['Compiler']='ifort'
        fullIfortPath = which('ifort')

        if(fullIfortPath == ''): sys.exit("No ifort found.")
        compilerFlags['ifort-openmp']['FCFLAGS1']="-O3 -fp-model source -e08 -free -qopenmp -assume byterecl,realloc_lhs -fPIC"
        compilerFlags['ifort-openmp']['FCFLAGS2']=""
        compilerFlags['ifort-openmp']['LDFLAGS']="-Wall -g -shared -lnetcdf -lnetcdff -lhdf5"
        compilerFlags['ifort-openmp']['F2PY_COMPILER']='intelem'
    elif(arch =='gfortran'):
        compilerFlags['gfortran']={}
        compilerFlags['gfortran']['Compiler']='gfortran'
        fullGfortranPath = which('gfortran')
        if(fullGfortranPath ==''): sys.exit("No gfortran found in path.")

        gccBinPath = os.path.split(fullGfortranPath)[0]
        gccPath = os.path.split(gccBinPath)[0]

        # bit to check what gcc version is available, if not > 6. Problem. exit.
        p = Popen(['gfortran','-dumpversion'], stdout = PIPE, stderr = PIPE) 
        p.wait()
        so,se = p.communicate() 
        if ( int(so.decode("utf-8").split('.')[0]) < 6 ):
            sys.exit("F2008 required. gcc >= 6")
        compilerFlags['gfortran']['FCFLAGS1']="-O3 -fimplicit-none -ffree-form -fno-second-underscore -frecord-marker=4 -funroll-loops -Wall -Wconversion -mieee-fp -fbounds-check -std=f2008 -fPIC"
        compilerFlags['gfortran']['FCFLAGS2']=""   
        compilerFlags['gfortran']['LDFLAGS']="-Wall -g -shared -lnetcdf -lnetcdff -lhdf5 "
        compilerFlags['gfortran']['F2PY_COMPILER']="gnu95"
   
    elif(arch == 'ifort'):
        compilerFlags['ifort']={}
        compilerFlags['ifort']['Compiler']='ifort'
        fullIfortPath = which('ifort')

        if(fullIfortPath == ''): sys.exit("No ifort found.")
        compilerFlags['ifort']['FCFLAGS1']="-O3 -fp-model source -e08 -free -assume byterecl,realloc_lhs -fPIC"
        compilerFlags['ifort']['FCFLAGS2']=""
        compilerFlags['ifort']['LDFLAGS']="-Wall -g -shared -lnetcdf -lnetcdff -lhdf5"
        compilerFlags['ifort']['F2PY_COMPILER']='intelem'


    else:
        sys.exit('Unknown compiler {}.'.format(arch))   
    return compilerFlags
    
def runAndCheckProcess(p, name, fo, fe, scriptDir):
    if(p.returncode>0):
        foname = fo.name
        fename = fe.name

        with open(os.path.join(scriptDir,foname),'r') as foOb:
            for l in foOb.readlines():
                print( l.strip() )

        with open(os.path.join(scriptDir,fename),'r') as feOb:
            for l in feOb.readlines():
                print( l.strip() )

        print("For more information about the install look in {}, and {}".format(fo.name,fe.name) )
        fo.close()
        fe.close()
        sys.exit(name+" failed.")


def configureCompileInstallCrtm( installLocation, fo, fe, scriptDir, ncpath, h5path ):
    # configure as one usually does
    #p = Popen(['make','clean'],stderr=fe,stdout=fo,shell=True)
    #p.wait()
    #runAndCheckProcess(p, "Make clean", fo, fe, scriptDir)

    p = Popen(['./configure','--prefix='+installLocation,'--disable-big-endian'],stderr=fe,stdout=fo)
    p.wait()
    runAndCheckProcess(p,"CRTM configure", fo, fe, scriptDir)

    p = Popen(['make','-j'+a.jproc],stderr=fe,stdout=fo,shell=True)
    p.wait()
    runAndCheckProcess(p, "Compiling CRTM", fo, fe, scriptDir)

    # skip make check 
    #p = Popen(['make', 'check'],stderr=fe,stdout=fo, shell=True)
    #p.wait()
    #runAndCheckProcess(p,"CRTM check", fo, fe, scriptDir)
    
    p = Popen(['make','install'],stderr=fe,stdout=fo)
    p.wait()        
    runAndCheckProcess(p,"CRTM install", fo, fe, scriptDir)


def moveCrtmCoefficients(srcDir, destDir): 

    if os.path.isdir(destDir):
        shutil.rmtree(destDir)

    endianness = ("{}_endian".format(sys.byteorder)).title()

    os.makedirs(destDir)
    counter = 0

    for root, dirs, files in os.walk(srcDir):
        for filename in files:
            if endianness in root or 'netCDF' in root:
                counter+=1
                shutil.copy2(os.path.join(root, filename), destDir)

    print("{} coefficient files copied to {}".format(counter, destDir))   

    return

def makeModule(fo, fe, scriptDir):
    # make pycrtm module

    os.chdir(scriptDir)

    p=Popen(['make', 'clean'],stderr=fe,stdout=fo)
    p.wait()
    runAndCheckProcess(p,'pycrtm make clean', fo, fe, scriptDir)
   
    p=Popen(['make'],stderr=fe,stdout=fo)
    p.wait()
    runAndCheckProcess(p,'pycrtm make', fo, fe, scriptDir)

def modifyOptionsCfg( filename, scriptDir ):
    with open( filename+'new' ,'w') as newFile:
        with open(os.path.join(scriptDir, filename), 'r') as oldFile:
            for l in oldFile:
                if('coeffs_dir' in l):
                    newFile.write(l.replace(l,'coeffs_dir = '+os.path.join(os.path.join(scriptDir,'crtm_coef_pycrtm'),'')+os.linesep))
                else:
                    newFile.write(l)
    os.rename(filename+'new', filename)
def which(name):
    found = 0 
    for path in os.getenv("PATH").split(os.path.pathsep):
        full_path = path + os.sep + name
        if os.path.exists(full_path):
            found = 1
            return full_path
    return ''


def main( a ):
    fo = open('pycrtm.stdo','w')
    fe = open('pycrtm.stde','w')
 
    arch = a.arch

    installPath = os.path.abspath(a.install)
    crtmRepos = os.path.abspath(a.rtpath)
    coefDir = os.path.abspath(a.coef)

    h5path_lib = os.path.abspath(a.h5path_lib)
    h5path_inc = os.path.abspath(a.h5path_inc)
    ncpath_lib = os.path.abspath(a.ncpath_lib)
    ncpath_inc = os.path.abspath(a.ncpath_inc)

    compilerFlags = selectCompilerFlags(arch)
    # set the required environment variables
    os.environ["FC"] = compilerFlags[arch]['Compiler']  
    os.environ['FCFLAGS']= compilerFlags[arch]['FCFLAGS1']
    os.environ['LIBS']="-L {} -lnetcdf -lnetcdff -L {} -lhdf5 -I {} -I {} ".format(ncpath_lib,
                                                                                   h5path_lib,
                                                                                   ncpath_inc,
                                                                                   h5path_inc)
    
    scriptDir = os.path.split(os.path.abspath(__file__))[0]
    os.chdir( crtmRepos )
    # get installed/to be installed crtm path based on repository version. 
    with open(os.path.join('src','CRTM_Version.inc'),'r') as f:
        line = f.readline()
        crtm_dir = 'crtm_'+line.split()[2].replace("'","")        
        print("CRTM dir name: {}".format(crtm_dir))
        print(os.getcwd())
        path2CRTM = os.path.abspath(os.path.join(os.getcwd(), '..', crtm_dir))
        print("Path to CRTM dir: {}".format(path2CRTM)      )
        if not os.path.exists(path2CRTM):
            raise NotADirectoryError("{} is not a valid directory".format(path2CRTM))
        
    # if we want to build crtm first.
    if(a.rtinstall):
        # go into crtm git repository directory

        print("Configuring/Compiling/Installing CRTM.")
        # configure, comile and install CRTM to the installPath
        configureCompileInstallCrtm( installPath, fo, fe, scriptDir, ncpath_lib, h5path_lib )
        print("Copying coefficients to {}".format( os.path.join(scriptDir,'crtm_coef_pycrtm') ) )   

        # make the coef directory along with the install location
        # copy coefficients 
        in_coef_dir = os.path.join(crtmRepos,'fix')
        out_coef_dir = os.path.join(coefDir,'crtm_coef_pycrtm')
        print("Copying coefficients to {}".format( out_coef_dir ) )   
        moveCrtmCoefficients( in_coef_dir, out_coef_dir  )

        # go back to script directory.
        os.chdir( scriptDir )
    else:
        # os.chdir( crtmRepos )
        in_coef_dir = os.path.join(crtmRepos,'fix')
        out_coef_dir = os.path.join(coefDir,'crtm_coef_pycrtm')
        print("Copying coefficients to {}".format( out_coef_dir ) )   
        moveCrtmCoefficients( in_coef_dir, out_coef_dir  )
        # go back to script directory.
        # os.chdir( scriptDir )

    print("Modifying crtm.cfg")
    modifyOptionsCfg( 'crtm.cfg', scriptDir )
    print("Making python module.")
    # build python module
    # Set compile environment variables.
    if(arch =='gfortran-openmp'):
        openmpLink = ' -lgomp'
    elif(arch =='ifort-openmp'):
        openmpLink = ' -liomp5'
    else:
        openmpLink = ''
    os.environ['FCFLAGS'] = os.environ['FCFLAGS'] + compilerFlags[arch]['FCFLAGS2']
    os.environ['FFLAGS'] = os.environ['FCFLAGS']
    os.environ['FC'] = compilerFlags[arch]['Compiler']
    os.environ['ILOC'] = path2CRTM
    os.environ['F2PY_COMPILER'] = compilerFlags[arch]['F2PY_COMPILER']
    os.environ['FORT'] = compilerFlags[arch]['Compiler']
    os.environ['NCINSTALL'] = ncpath_lib
    os.environ['H5INSTALL'] = h5path_lib
    os.environ['DASHL'] = ' -lcrtm -lnetcdf -lnetcdff -lhdf5' + openmpLink

    makeModule(fo, fe, scriptDir)
    print('Changing back to {}'.format(scriptDir))
    os.chdir(scriptDir)
    modifyOptionsCfg( 'crtm.cfg', scriptDir ) 
    fo.close()
    fe.close()

    # replace numpy np.int depricated statement
    # Read in the file
    with open('pyCRTM.py', 'r') as f :
        filedata = f.read()

    # Replace the target string
    filedata = filedata.replace('np.int', 'np.int32')

    # Write the file out again
    with open('pyCRTM.py', 'w') as file:
        file.write(filedata)

    print("\n=======  PyCRTM install completed!  =======\n")
   
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = "install pycrtm, optionally crtm if it isn't built already.")
    parser.add_argument('--install',help = 'CRTM install path.', required = True, dest='install')
    parser.add_argument('--repos',help = 'path to CRTM github clone.', required = True, dest='rtpath')
    parser.add_argument('--coef',help = 'path to place crtm_coef_pycrtm directory.', required = True, dest='coef')
    parser.add_argument('--ncpath_lib',help = 'path to NETCDF install.', required = True, dest='ncpath_lib')
    parser.add_argument('--ncpath_inc',help = 'path to NETCDF install.', required = True, dest='ncpath_inc')
    parser.add_argument('--h5path_lib',help = 'path to H5 install.', required = True, dest='h5path_lib')
    parser.add_argument('--h5path_inc',help = 'path to H5 install.', required = True, dest='h5path_inc')
    parser.add_argument('--jproc',help = 'Number of threads to pass to make.', required = True, dest='jproc')
    parser.add_argument('--arch',help = 'compiler/architecture.', required = False, dest='arch', default='gfortran-openmp')
    parser.add_argument('--inplace', help="Switch installer to use rtpath for previously installed crtm.", dest='rtinstall', action='store_false' )
    a = parser.parse_args()
    main(a)
