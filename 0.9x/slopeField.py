#!/usr/bin/python

from math import *

import inkscapeMadeEasy_Base as inkBase
import inkscapeMadeEasy_Draw as inkDraw
import inkscapeMadeEasy_Plot as inkPlot
import numpy

import inkex


# heaviside function
def u(x):
    if x < 0:
        return 0.0
    else:
        return 1.0


# rectangular Pulse
def rectPulse(x, amplitude=1.0, lenght=1.0, offset=0.0, delay=0.0):
    return amplitude * (u(x - delay) - u(x - lenght - delay)) + offset


# square wave, with amplitude -A/2 to A/2, and given period
def squareWave(x, amplitude=1.0, offset=0, period=1.0, delay=0.0):
    return rectPulse((x % period), amplitude, period / 2.0, offset=-amplitude / 2.0 + offset, delay=delay)


# ---------------------------------------------
class PlotSlopeField(inkBase.inkscapeMadeEasy):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option("--tab", action="store", type="string", dest="tab", default="object")

        self.OptionParser.add_option("--function", action="store", type="string", dest="function", default='x*x-y*y')
        self.OptionParser.add_option("--generalAspectFactor", action="store", type="float", dest="generalAspectFactor", default=1.0)
        self.OptionParser.add_option("--xMin", action="store", type="float", dest="xMin", default='0.0')
        self.OptionParser.add_option("--xMax", action="store", type="float", dest="xMax", default='0.0')
        # self.OptionParser.add_option("--xPi", action="store", type="inkbool", dest="xPi", default=False)
        self.OptionParser.add_option("--yMin", action="store", type="float", dest="yMin", default='0.0')
        self.OptionParser.add_option("--yMax", action="store", type="float", dest="yMax", default='0.0')
        # self.OptionParser.add_option("--yPi", action="store", type="inkbool", dest="yPi", default=False)

        self.OptionParser.add_option("--xLabel", action="store", type="string", dest="xLabel", default='')
        self.OptionParser.add_option("--xScale", action="store", type="float", dest="xScale", default='5')
        self.OptionParser.add_option("--xTicks", action="store", type="inkbool", dest="xTicks", default=False)
        self.OptionParser.add_option("--xTickStep", action="store", type="float", dest="xTickStep", default='1')
        self.OptionParser.add_option("--xGrid", action="store", type="inkbool", dest="xGrid", default=True)
        # self.OptionParser.add_option("--xExtraText", action="store", type="string", dest="xExtraText", default='')

        self.OptionParser.add_option("--yLabel", action="store", type="string", dest="yLabel", default='')
        self.OptionParser.add_option("--yScale", action="store", type="float", dest="yScale", default='5')
        self.OptionParser.add_option("--yTicks", action="store", type="inkbool", dest="yTicks", default=False)
        self.OptionParser.add_option("--yTickStep", action="store", type="float", dest="yTickStep", default='1')
        self.OptionParser.add_option("--yGrid", action="store", type="inkbool", dest="yGrid", default=True)

        self.OptionParser.add_option("--nSegmentsX", action="store", type="int", dest="nSegmentsX", default=10)
        self.OptionParser.add_option("--nSegmentsY", action="store", type="int", dest="nSegmentsY", default=10)
        self.OptionParser.add_option("--segmentAspectFactor", action="store", type="float", dest="segmentAspectFactor", default=1.0)
        self.OptionParser.add_option("--slopeColor", action="store", type="string", dest="slopeColor", default='#FF0000')
        self.OptionParser.add_option("--slopeColorPicker", action="store", type="string", dest="slopeColorPicker", default='0')


    def effect(self):

        so = self.options

        # sets the position to the viewport center
        position = [self.view_center[0], self.view_center[1]]
        position[0] = int(ceil(position[0] / 10.0)) * 10
        position[1] = int(ceil(position[1] / 10.0)) * 10

        [self.slopeColor, alpha] = inkDraw.color.parseColorPicker(so.slopeColor, so.slopeColorPicker)

        # root_layer = self.current_layer
        root_layer = self.document.getroot()
        # root_layer = self.getcurrentLayer()

        # generate xy data
        xVals = numpy.linspace(so.xMin, so.xMax, so.nSegmentsX)
        yVals = numpy.linspace(so.yMin, so.yMax, so.nSegmentsY)
        xlength=(xVals[1]-xVals[0])
        ylength=(yVals[1]-yVals[0])
        radius = min( xlength * (so.xScale / so.xTickStep), ylength * (so.yScale / so.yTickStep)) * 1.0 / 2.0

        # eval function
        slopeFunction = eval('lambda x,y: ' + so.function)
        slope = numpy.zeros((len(xVals), len(yVals)))

        for i in range(len(xVals)):
            for j in range(len(yVals)):
                slope[i][j] = slopeFunction(xVals[i], yVals[j])

        # line style
        lineWidthPlot = so.segmentAspectFactor * so.generalAspectFactor * min(so.xScale, so.yScale) / 60.0
        lineStylePlot = inkDraw.lineStyle.set(lineWidth=lineWidthPlot, lineColor=self.slopeColor)

        textSize = so.generalAspectFactor * 0.25 * min(so.xScale, so.yScale)
        lineWidthAxis = so.generalAspectFactor * min(so.xScale, so.yScale) / 35.0
        slopePlot = self.createGroup(root_layer, 'PlotData')

        inkPlot.axis.cartesian(self, slopePlot, [so.xMin, so.xMax], [so.yMin, so.yMax], position, xLabel=so.xLabel,
                               yLabel=so.yLabel, xTicks=so.xTicks, yTicks=so.yTicks, xTickStep=so.xTickStep,
                               yTickStep=so.yTickStep, xScale=so.xScale, yScale=so.yScale, xGrid=so.xGrid,
                               yGrid=so.yGrid,forceTextSize=textSize,forceLineWidth=lineWidthAxis)




        slopeData = self.createGroup(slopePlot, 'PlotData')


        for i in range(len(xVals)):
            xc = xVals[i] * (so.xScale / so.xTickStep)
            for j in range(len(yVals)):
                yc = -yVals[j] * (so.yScale / so.yTickStep)
                theta = atan(slope[i][j] * (so.yScale / so.yTickStep) / (so.xScale / so.xTickStep))
                deltaX = radius * cos(theta)  # *(so.xScale/so.xTickStep)
                deltaY = -radius * sin(theta)  # *(so.yScale/so.yTickStep)
                points = [[xc - deltaX, yc - deltaY], [xc, yc], [xc + deltaX, yc + deltaY]]
                inkDraw.line.absCoords(slopeData, points, [position[0], position[1]], lineStyle=lineStylePlot)


if __name__ == '__main__': #
    plot = PlotSlopeField()
    plot.affect()
