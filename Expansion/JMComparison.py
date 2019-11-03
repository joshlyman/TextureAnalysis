from JMDistance import JMDistance
import numpy

GLCM_0_Data = numpy.genfromtxt('GLCM_0.csv', delimiter = ',')
GLCM_0_Feature = GLCM_0_Data[1:, :-1]
GLCM_0_Result = GLCM_0_Data[1:,GLCM_0_Data.shape[1] - 1]

GLCM_45_Data = numpy.genfromtxt('GLCM_45.csv', delimiter = ',')
GLCM_45_Feature = GLCM_45_Data[1:, :-1]
GLCM_45_Result = GLCM_45_Data[1:,GLCM_45_Data.shape[1] - 1]

GLCM_90_Data = numpy.genfromtxt('GLCM_90.csv', delimiter = ',')
GLCM_90_Feature = GLCM_90_Data[1:, :-1]
GLCM_90_Result = GLCM_90_Data[1:,GLCM_90_Data.shape[1] - 1]

GLCM_135_Data = numpy.genfromtxt('GLCM_135.csv', delimiter = ',')
GLCM_135_Feature = GLCM_135_Data[1:, :-1]
GLCM_135_Result = GLCM_135_Data[1:,GLCM_135_Data.shape[1] - 1]

GLCM_Avg_Data = numpy.genfromtxt('GLCM_Avg.csv', delimiter = ',')
GLCM_Avg_Feature = GLCM_Avg_Data[1:, :-1]
GLCM_Avg_Result = GLCM_Avg_Data[1:,GLCM_Avg_Data.shape[1] - 1]

print JMDistance(GLCM_0_Feature, GLCM_0_Result)
#print JMDistance(GLCM_45_Feature, GLCM_45_Result)
#print JMDistance(GLCM_90_Feature, GLCM_90_Result)
#print JMDistance(GLCM_135_Feature, GLCM_135_Result)
#print JMDistance(GLCM_Avg_Feature, GLCM_Avg_Result)
