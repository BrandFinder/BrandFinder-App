import cv2 as cv
import numpy as np
import imutils
import numpy as np

colors_dict = {
    'negro': [0, 0, 0],
    'blanco': [255, 255, 255],
    'rojo': [255, 0, 0],
    'verde': [0, 255, 0],
    'azul': [0, 0, 255],
    'amarillo': [255, 255, 0],
    'magenta': [255, 0, 255],
    'cian': [0, 255, 255]
}

def R_measure(image):

    norm_var = image.var()/255 # Obtenemos la varianza de la imagen y la normalizamos
    R = 1 - (1 / (1 + norm_var)) # Aplicamos la fórmula para calcular R a partir de la varianza normalizada

    return R

def segment_car_by_color(image, color_name, hue_tolerance = 25, k = 10, r_measure = 0.92):

    def get_mask(target_color_hsv, hue_tolerance):

        if color_name.lower() == 'negro':
            lower = np.array([0, 0, 0])
            upper = np.array([179, 255, 50])
            full_mask = cv.inRange(hsv, lower, upper)
            return full_mask
        elif color_name.lower() == 'blanco':
            lower = np.array([0, 0, 200])
            upper = np.array([179, 30, 255])
            full_mask = cv.inRange(hsv, lower, upper)
            return full_mask
        elif color_name.lower() == 'gris':
            lower = np.array([0, 0, 100])
            upper = np.array([179, 30, 200])
            full_mask = cv.inRange(hsv, lower, upper)
            return full_mask
        
        lower_hue = target_color_hsv[0][0][0] - hue_tolerance
        upper_hue = target_color_hsv[0][0][0] + hue_tolerance
            
        if lower_hue < 0:
            lower1 = np.array([0, 100, 100])
            upper1 = np.array([upper_hue, 255, 255])
            
            lower2 = np.array([179 + lower_hue, 100, 100])
            upper2 = np.array([179, 255, 255])
            
            lower_mask = cv.inRange(hsv, lower1, upper1)
            upper_mask = cv.inRange(hsv, lower2, upper2)
            full_mask = lower_mask + upper_mask
            
        elif upper_hue > 179:
            
            lower1 = np.array([0, 100, 100])
            upper1 = np.array([upper_hue - 179, 255, 255])
            
            lower2 = np.array([lower_hue, 100, 100])
            upper2 = np.array([179, 255, 255])
            
            lower_mask = cv.inRange(hsv, lower1, upper1)
            upper_mask = cv.inRange(hsv, lower2, upper2)
            full_mask = lower_mask + upper_mask
            
            
        else: # lower_hue >= 0 and upper_hue <= 179
        
            lower = np.array([lower_hue, 100, 100])
            upper = np.array([upper_hue, 255, 255])
            full_mask = cv.inRange(hsv, lower, upper)
            
        return full_mask
    
    # if the color_name is not in colors_dict, we skip the image we are processing
    if color_name.lower() not in colors_dict:
        return None
    
    # if the image is too similar to the background, we skip it
    if R_measure(image) < r_measure:    
        return None

    target_color = colors_dict[color_name.lower()]
    
    # Convertir la imagen a RGB
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    # Convertir la imagen a valores de píxeles individuales
    pixel_values = image.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)

    # Realizar K-means clustering para encontrar los centros de los colores similares al objetivo
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    
    _, labels, (centers) = cv.kmeans(pixel_values, k, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

    # Convertir los centros a enteros sin signo de 8 bits y aplanar las etiquetas
    centers = np.uint8(centers)
    labels = labels.flatten()

    # Crear una imagen segmentada donde cada píxel está etiquetado con el centro más cercano
    segmented_image = centers[labels.flatten()]
    segmented_image = segmented_image.reshape(image.shape)
    
    # Convertir la imagen segmentada a HSV
    hsv = cv.cvtColor(segmented_image, cv.COLOR_RGB2HSV)

    # Definir los límites superior e inferior del color objetivo en HSV
    target_color_hsv = cv.cvtColor(np.uint8([[target_color]]), cv.COLOR_RGB2HSV)

    full_mask = get_mask(target_color_hsv, hue_tolerance)
    
    # Aplicar la máscara a la imagen original
    masked_image = cv.bitwise_and(segmented_image, segmented_image, mask=full_mask)
    
    contours, _ = cv.findContours(full_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv.contourArea)
        # Encontrar la caja delimitadora del contorno más grande y devolver la región recortada de la imagen original
        x, y, w, h = cv.boundingRect(largest_contour)
        return segmented_image, masked_image, largest_contour, image[y:y+h, x:x+w]
    else:
        return None
    
def detect_car_brand(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.bilateralFilter(gray, 13, 15, 15)
    edged = cv.Canny(gray, 30, 200)
    contours=cv.findContours(edged.copy(),cv.RETR_TREE,
                                                cv.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours,key=cv.contourArea, reverse = True)[:10]
    screenCnt = None
    value = False

    for c in contours:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            value = True
            break
            
    if not value:
        return None
    
    x,y,w,h = cv.boundingRect(screenCnt)
    upper_region = img[y-h-h-h:y, x:x+w]
    


    return upper_region

def get_car_brand(image, color):
    try:
        image_path = "media/" + str(image)
        car = cv.imread(image_path)
        _,_,_, car_segmented = segment_car_by_color(car, color)
        car_brand = detect_car_brand(car_segmented)

        return car_brand
    except Exception as e:
        print(e)
        return None