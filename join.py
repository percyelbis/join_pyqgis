
'''
todos los shp tienen que corregirse geometricamnete
'''
#capas del canvas
epsg = 32718
capa_puntos = ['ANN_HU', 'ANN_TG_MZ_URB', 'ANN_TG_LT_URB' ]
capa_poligonos = ['TG_HU', 'TG_MZ_URB', 'TG_LT_URB']
#csv
csv = 'rentas'
id_csv = 'ID_LOTE_URB'
# salidas
salida_carpeta = r'C:\Users\user\Desktop\resultados'
# Las id de cada campo
txt = 'Text_'
# expresion
exp = "aggregate(layer:='TG_HU_join', aggregate:='concatenate', expression:= \"Text_\" , filter:=intersects( $geometry, centroid(geometry(@parent) ) )) || aggregate(layer:='TG_MZ_URB_join', aggregate:='concatenate', expression:= \"Text_\" , filter:=intersects( $geometry, centroid(geometry(@parent) ) )) ||  \"Text_\""


#............ pyqgis ........
temp = []
for i in range(len(capa_poligonos)):
    polygon_layer = QgsProject.instance().mapLayersByName(capa_poligonos[i])[0]
    point_layer = QgsProject.instance().mapLayersByName(capa_puntos[i])[0]
    output_path = salida_carpeta + "\\" + capa_poligonos[i] + "_join" + ".gpkg"

    # Join
    processing.run(
    "native:joinattributesbylocation",
    {'INPUT':polygon_layer,
    'JOIN':point_layer,
    'PREDICATE':[0],
    'JOIN_FIELDS':[txt],
    'METHOD':0,
    'DISCARD_NONMATCHING':False,
    'PREFIX':'',
    'OUTPUT':output_path})
    temp.append(output_path)
    layer = QgsVectorLayer(output_path, capa_poligonos[i] + "_join", "ogr")
    layer.setCrs(polygon_layer.crs())
    crs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
    layer.setCrs(crs)
    if not layer.isValid():
      print("El archivo no es válido")
    else:
      QgsProject.instance().addMapLayer(layer)


# Crear el nuevo atributo en la capa
mi_capa = QgsProject.instance().mapLayersByName("TG_LT_URB_join")[0]
mi_capa.startEditing()
mi_capa.addAttribute(QgsField("idrentas", QVariant.String))

mi_capa.commitChanges()


expression = QgsExpression(exp)
context = QgsExpressionContext()
mi_capa.startEditing()
for feature in mi_capa.getFeatures():
    context.setFeature(feature)
    idrentas = expression.evaluate(context)
    feature['idrentas'] = idrentas
    mi_capa.updateFeature(feature)
mi_capa.commitChanges()




# join final
mi_csv = QgsProject.instance().mapLayersByName(csv)[0]
result = processing.run("native:joinattributestable", 
    {'INPUT':mi_capa,
    'FIELD':'idrentas',
    'INPUT_2':mi_csv,
    'FIELD_2':id_csv,
    'FIELDS_TO_COPY':[],
    'METHOD':1,
    'DISCARD_NONMATCHING':False,
    'PREFIX':'',
    'OUTPUT':salida_carpeta +'\TG_LOTE_FINAL.gpkg'})

# limpiar canvas
QgsProject.instance().removeAllMapLayers()
# anadir join final
layer = QgsVectorLayer(result['OUTPUT'], 'TG_LOTE_FINAL', 'ogr')
QgsProject.instance().addMapLayer(layer)

iface.messageBar().pushMessage("qgis", "Fue todo un exito!!!", level=Qgis.Info, duration=3)



