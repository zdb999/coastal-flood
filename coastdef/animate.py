"""Note that this module is full of script-like stuff, and
is not prepared for public use. It is a work in progress."""

import cv2
import numpy as np
from osgeo import gdal, gdalnumeric, ogr, osr
from cv2 import VideoWriter
from PIL import ImageFont, ImageDraw, Image
import utils
import geo
import lib
gdal.UseExceptions()


def add_text_overlay(image, text, origin, size, font, color):
  # Load image in OpenCV  
    
   # Convert the image to RGB (OpenCV uses BGR)
   cv2_im_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)  
     
   # Pass the image to PIL  
   pil_im = Image.fromarray(cv2_im_rgb)
     
   draw = ImageDraw.Draw(pil_im)  
   # use a truetype font  
   font = ImageFont.truetype(font, size)  
     
   # Draw the text  
   draw.text(origin, text, font=font, fill=color)  
     
   # Get back the image to OpenCV  
   return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)


def animate_flood(dem_path, water_points, low, high, step, duration):

  # Open DEM layer

  raster, img, projection, transform = utils.import_dem(dem_path)

  # TODO: implement water points, change this

  points = water_points

  # Load numpy version of image and load xy coorinates

  h,w = np.shape(img)

  # Calculate frame rate
  seconds = duration
  FPS = int((high - low) / float(step * duration))

  # Encode and name
  fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
  video = VideoWriter('./out.avi', fourcc, FPS, (w, h))

  frame = np.full((h,w,3), 255, np.uint8)

  # Generate first frame
  frame = np.full((h,w,3), 255, np.uint8)

  # Create and write frames
  for i in range(FPS*seconds):
      frame[:,:,1] = geo.flood_extent(img, points, low + i*step)
      if i == 0:
        frame[:,:,2] = geo.flood_extent(img, points, low + i*step)

      out_str = str(i/10.) + " ft"
      text_frame = add_text_overlay(frame, out_str, (4500,3500), 400, "./fonts/Vera.ttf", (255,255,255))
      # cv2.putText(frame,'Water flooding',(300,300), font, 50,(255,255,255),2,lineType=3)
      # cv2.circle(text_frame,(5000, 4000), 63, (0,0,255), -1)
      video.write(text_frame)
      frame[:,:,2] = frame[:,:,1]
  video.release()

def binary_overlay(top, bottom):
  out = top
  out = np.where(out == 255, out, bottom)
  return out


def animate_flood2(dem_path, water_points, low, high, step, duration):

  # Open DEM layer

  raster, img, projection, transform = utils.import_dem(dem_path)

  # TODO: implement water points, change this

  points = water_points


  # Load numpy version of image and load xy coorinates

  h,w = np.shape(img)

  # Calculate frame rate
  seconds = duration
  FPS = int((high - low) / float(step * duration))

  # Encode and name
  fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
  video = VideoWriter('./out.avi', fourcc, FPS, (w, h))

  # Generate first frame

  frame = np.full((h,w,3), 255, np.uint8)

  back = cv2.imread('sample_data/Seaside.tif')
  # Create and write frames
  for i in range(FPS*seconds):

      extent = geo.flood_extent(img, points, low + i*step)
      extent2 = geo.flood_extent(img, points, low + 1 + i*step)
      # frame = back
      # # frame     
      # frame[:,:,1] = extent
      # if i == 0:
      #   frame[:,:,2] = extent
      frame[np.where(extent2 == 0)] = [51, 118, 165]
      frame[np.where(extent == 0)] = [165, 123, 51]
      # insert = back[np.where(frame == 255)]
      # frame[np.where(frame == 255)] = insert
      out_str = str(i/10.) + " ft"
      text_frame = add_text_overlay(frame, out_str, (1200,600), 65, "fonts/Vera.ttf", (255,255,255))
      out_frame = cv2.addWeighted(text_frame, .7, back, .3, 0)
      # cv2.putText(frame,'Water flooding',(300,300), font, 50,(255,255,255),2,lineType=3)
      # cv2.circle(text_frame,(5000, 4000), 63, (0,0,255), -1)
      # out_frame = out_frame[2:w-2,2:h-2,:]
      video.write(out_frame)
      frame[:,:,2] = frame[:,:,1]
  video.release()


def animate_flood3(dem_path, water_points, low, high, step, duration):



  # Open DEM layer

  raster, img, projection, transform = utils.import_dem(dem_path)

  # TODO: implement water points, change this

  points = water_points


  # Load numpy version of image and load xy coorinates

  h,w = np.shape(img)

  # Calculate frame rate
  seconds = duration
  FPS = int((high - low) / float(step * duration))

  # Encode and name
  fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
  video = VideoWriter('./out.avi', fourcc, FPS, (w, h))

  # Generate first frame

  frame = np.full((h,w,3), 255, np.uint8)

  back = cv2.imread('sample_data/Seaside.tif')
  over = cv2.imread('sample_data/overlay.png')

  surge = 1.
  # Create and write frames
  for y in range(low, high, 1):
      extentl = geo.flood_extent(img, points, 10*(surge + lib.noaa_global_low(y)))
      extentml = geo.flood_extent(img, points, 10*(surge + lib.noaa_global_intermed_low(y)))
      extentmh = geo.flood_extent(img, points, 10*(surge + lib.noaa_global_intermed_high(y)))
      extenth = geo.flood_extent(img, points, 10*(surge + lib.noaa_global_high(y)))

      frame[np.where(extenth == 0)] = [95, 165, 61]
      frame[np.where(extentmh == 0)] = [69, 154, 156]
      frame[np.where(extentml == 0)] = [77, 77, 179]
      frame[np.where(extentl == 0)] = [173, 80, 52]

      out_str = str(y)
      text_frame = add_text_overlay(frame, out_str, (850,700), 65, "fonts/Vera.ttf", (255,255,255))
      out_frame = cv2.addWeighted(text_frame, .7, back, .3, 0)

      out_frame[np.where(over[:,:,1] != 255)] = over[np.where(over[:,:,1] != 255)]
      video.write(out_frame)
      frame[:,:,2] = frame[:,:,1]
  video.release()