/*A program to take single images as well as tdi for FilterSpec */

#include <stdlib.h>
#include "fitsio.h"
#include <math.h>
#include <unistd.h>
#include <time.h>
#include "tcl.h"
#include "ApnCamera.h"
#include "ccd.h"
#include <string.h>
#include <iostream>
#include <stdio.h>

using namespace std;

int tdi(char *imtype, char *imagename, char *rate);
int temp(double cam_temp);
int singe_image(char *imagename, double exposure, int shutter);
int saveimage(unsigned short *src_buffer, char *filename, short nx, short ny);
int stop();
int startDriver();

CApnCamera *alta = (CApnCamera *)new CApnCamera();


/*global variables*/
double cam_temp=20.0;
char imagename[256];
double exposure=1.0;
int shutter=1;
char rate;
int xbin=1;
int ybin=1;
int xstart=0;
int xend=0;
int ystart=0;
int yend=0;
int biascols=0;
int fanmode=2;
int numexp=1;

/* Bias definitions used in the libccd functions */
extern int bias_start, bias_end, bcols;

/* Functions from libccd, provide simple named image buffer management */
typedef struct {
     unsigned short *pixels;
     int            size;
     short          xdim;
     short          ydim;
     short          zdim;
     long           xbin;
     long           ybin;
     short          type;
     char           name[64];
     int            shmid;
     size_t         shmsize;
     char           *shmem;
} CCD_FRAME;

typedef void *PDATA;
#define MAX_CCD_BUFFERS  1000
PDATA CCD_locate_buffer(char *name, int idepth, short imgcols, short imgrows, short hbin, short vbin);
int   CCD_free_buffer();
int   CCD_locate_buffernum(char *name);
extern CCD_FRAME CCD_Frame[MAX_CCD_BUFFERS];
extern int CCD_free_buffer(char *name);

int main(int argc, char *args[])
{
  int tdi(char *imtype, char *imagename, char *rate);
  int single_image(char *imagename, double exposure, int shutter);
  int temp(double cam_temp);
  int saveimage(unsigned short *src_buffer, char *filename, short nx, short ny);
  int stop();
  int startDriver();
  int status();
  bool quit=false;
  char str[80];
  char var1[80];
  char var2[80];
  char var3[80];
  
  

  alta->InitDriver(1,0,0);

  while (!quit){    
    scanf("%s %s %s %s", str, var1, var2, var3);
    cout << str <<' ' <<var1<<' '<<var2<<' '<<var3<<endl;
    if (strcmp(str,"test")==0){
      cout << "acknowledge test" << endl;
    } else if (strcmp(str,"tdi")==0){
      tdi(var1, var2, var3);
    } else if (strcmp(str,"image")==0){
      // image, exposure, shutter
      single_image(var1,atof(var2),atof(var3));
    } else if (strcmp(str,"stopDriver")==0){
      stop();
    } else if (strcmp(str,"startDriver")==0){
      startDriver();
    } else if (strcmp(str,"exit")==0){
      alta->CloseDriver();
      quit=true;
    } else if (strcmp(str,"status")==0){
      status();
    }
  }
  //alta->CloseDriver();
}

int startDriver(){
  alta->InitDriver(1,0,0);
  return(0);
}

int stop(){
  alta->CloseDriver();
}

int status(){
  cout<< "Cooler Enabled: "<< alta->read_CoolerEnable() <<endl;
  cout <<"CCD Temp Set point: "<< alta->read_CoolerSetPoint() <<endl;
  cout << "CCD Temp: " << alta->read_TempCCD() <<endl;
  return(0);
}

int temp(double cam_temp)
{
  double t; 
  alta->ResetSystem(); 
  alta->write_FanMode(3);
  cout<<"Waiting for requested temperature of "<< cam_temp <<endl;
  alta->write_CoolerEnable(1);
  alta->write_CoolerSetPoint(cam_temp);
  t = alta->read_TempCCD();
	   
  while (fabs(t-cam_temp) > 0.2 or t < cam_temp) { 
    cout << "Waiting for requested temperature of" << cam_temp <<", current value is" << t <<endl;
    sleep(1);
    t = alta->read_TempCCD();
  }
  cout << "The Temperature is now " << t << endl ;  
}

int single_image(char *imagename, double exposure, int shutter)
{
  int nx,ny;
  int status;
  unsigned short *image;
  int bnum,i;
 
  alta->ResetSystem(); 
  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;
  if (xstart > 0) {
          alta->m_pvtRoiStartX = xstart;
          alta->m_pvtRoiStartY = ystart;
          alta->m_pvtRoiPixelsH = (xend-xstart+1);
          alta->m_pvtRoiPixelsV = (yend-ystart+1);
  }

  alta->m_pvtRoiPixelsH = alta->m_pvtRoiPixelsH / xbin;
  alta->m_pvtRoiPixelsV = alta->m_pvtRoiPixelsV / ybin;
  alta->write_RoiBinningH (xbin);
  alta->write_RoiBinningV (ybin);

  alta->write_RoiBinningH(xbin);
  alta->write_RoiBinningV(ybin);
  alta->write_ImageCount(1);

  status = alta->Expose(exposure,shutter);
  sleep(exposure+1);

  status = alta->BufferImage("tempobs"); 
  bnum = CCD_locate_buffernum("tempobs");
  image = CCD_Frame[bnum].pixels;
  nx = CCD_Frame[bnum].xdim;
  ny = CCD_Frame[bnum].ydim;

  saveimage(image, imagename, nx, ny);

  alta->ResetSystem();
  alta->ResetSystemNoFlush();
  alta->ResetSystem();

  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;


}

int tdi(char *imtype, char *imagename, char *rate)
{
  int shutter = 1;
  int i, bnum;
  int status;
  unsigned short *image;
  int nx,ny;
  //double ccd_rate;
  
  if (strcmp(imtype, "dark")==0)
    {
      shutter=0;
	} else {
    shutter =1;
      }
      
  alta->ResetSystem();
  i=0;
  if (xstart > 0) {
          alta->m_pvtRoiStartX = xstart;
          alta->m_pvtRoiStartY = ystart;
          alta->m_pvtRoiPixelsH = (xend-xstart+1);
          alta->m_pvtRoiPixelsV = (yend-ystart+1);
  }
  alta->m_pvtRoiPixelsH = alta->m_pvtRoiPixelsH / xbin;
  alta->m_pvtRoiPixelsV = alta->m_pvtRoiPixelsV / ybin;
  alta->write_RoiBinningH(xbin);
  alta->write_RoiBinningV(ybin);

  alta->write_RoiBinningH(xbin);
  alta->write_RoiBinningV(ybin);
  alta->write_ImageCount(1);

  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;

  //tdi setup
  int pix=3200;
  double ccd_rate=.0125/4;
  /*if (strcmp(rate, "1")==0){
    double ccd_rate=.0125/4;
  } else if (strcmp(rate,"2")==0){
    double ccd_rate=0.003125;
  }else if (strcmp(rate,"3")==0){
    double ccd_rate=0.0125;
    }*/
  alta->m_pvtRoiPixelsV = pix;
  alta->write_TDIRows (pix);
  alta->write_TDIRate (ccd_rate);
  alta->write_CameraMode (Apn_CameraMode_TDI);
  alta->write_SequenceBulkDownload (true);
  
  status = alta->Expose(pix*ccd_rate,shutter);
  sleep(pix*ccd_rate+2);

  cout << alta->read_ImagingStatus() << endl;

  // while (alta->read_ImagingStatus() != Apn_Status_ImageReady);


  status = alta->BufferImage("tempobs"); 
  bnum = CCD_locate_buffernum("tempobs");

  cout <<status<<endl;
  cout<<bnum<<endl;

  image = CCD_Frame[bnum].pixels;
  nx = CCD_Frame[bnum].xdim;
  ny = CCD_Frame[bnum].ydim;

  saveimage(image, imagename, nx, ny);


  alta->ResetSystem();
  alta->ResetSystemNoFlush();
  alta->ResetSystem();

  alta->CloseDriver();

  alta->InitDriver(1,0,0);
  

  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;

  }

 /*int tdi(char *imtype, char *imagename, char *rate)
{
  int shutter = 1;
  int i, bnum;
  int status;
  unsigned short *image;
  int nx,ny;

  FILE* filePtr;
  unsigned short* pBuffer;
  unsigned long ImgSizeBytes;
  char szFilename[80];
  
  if (strcmp(imtype, "dark")==0)
    {
      shutter=0;
	} else {
    shutter =1;
      }
      
  alta->ResetSystem();
  i=0;
  if (xstart > 0) {
          alta->m_pvtRoiStartX = xstart;
          alta->m_pvtRoiStartY = ystart;
          alta->m_pvtRoiPixelsH = (xend-xstart+1);
          alta->m_pvtRoiPixelsV = (yend-ystart+1);
  }
  alta->m_pvtRoiPixelsH = alta->m_pvtRoiPixelsH / xbin;
  alta->m_pvtRoiPixelsV = alta->m_pvtRoiPixelsV / ybin;
  alta->write_RoiBinningH(xbin);
  alta->write_RoiBinningV(ybin);

  alta->write_RoiBinningH(xbin);
  alta->write_RoiBinningV(ybin);
  alta->write_ImageCount(1);

  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;

  //tdi setup
  int pix=6400;
  double ccd_rate=.00625;

  // Set the image size
  long ImgXSize = alta->m_ApnSensorInfo->m_ImagingColumns;
  long ImgYSize = pix;             // Since SequenceBulkDownload = true

  pBuffer         = new unsigned short[ ImgXSize * ImgYSize];
  ImgSizeBytes    = ImgXSize * ImgYSize * 2;

  filePtr = fopen( szFilename, "wb" );
  if ( filePtr == NULL )
    {
      printf( "ERROR:  Failed to open output file.  No file will be written." );
    }

    
  alta->m_pvtRoiPixelsV = pix;
  alta->write_TDIRows (pix);
  alta->write_TDIRate (ccd_rate);
  alta->write_CameraMode (Apn_CameraMode_TDI);
  alta->write_SequenceBulkDownload (true);
  
  status = alta->Expose(pix*ccd_rate,shutter);
  sleep(pix*ccd_rate+2);

  cout << alta->read_ImagingStatus() << endl;

  while (alta->read_ImagingStatus() != Apn_Status_ImageReady);

  alta->GetImage( pBuffer );


  status = alta->BufferImage("tempobs"); 
  bnum = CCD_locate_buffernum("tempobs");

  image = CCD_Frame[bnum].pixels;
  nx = CCD_Frame[bnum].xdim;
  ny = CCD_Frame[bnum].ydim;

  //saveimage(image, imagename, nx, ny);


  alta->ResetSystem();
  alta->ResetSystemNoFlush();
  alta->ResetSystem();

  alta->InitDriver(1,0,0);
  

  cout << "Imaging Status "<< alta->read_ImagingStatus() << endl;

}*/

int saveimage(unsigned short *src_buffer, char *filename, short nx, short ny)
{
  fitsfile *fptr;       /* pointer to the FITS file, defined in fitsio.h */
  long  fpixel, nelements;
  unsigned short *array;
  unsigned short *simg;
  int status;
  /* initialize FITS image parameters */
  int bitpix   =  USHORT_IMG; /* 16-bit unsigned short pixel values       */
  long naxis    =   2;  /* 2-dimensional image                            */
  long naxes[2];   
  naxes[0] = nx-bcols;
  naxes[1] = ny; 
  array = src_buffer;
  status = 0;         /* initialize status before calling fitsio routines */
  simg = (unsigned short *)CCD_locate_buffer("stemp",2,nx-bcols,ny,1,1);
  if (fits_create_file(&fptr, filename, &status)) /* create new FITS file */
    printerror( status );           /* call printerror if error occurs */ 
  if ( fits_create_img(fptr,  bitpix, naxis, naxes, &status) )
    printerror( status );
  fpixel = 1;                               /* first pixel to write      */
  nelements = naxes[0] * naxes[1];          /* number of pixels to write */
  if ( fits_write_img(fptr, TUSHORT, fpixel, nelements, src_buffer, &status) )
    printerror( status );
  
  if ( fits_close_file(fptr, &status) )                /* close the file */
    printerror( status );
  return(status);
}                                                                              
