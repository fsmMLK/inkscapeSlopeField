#!/usr/bin/python

from math import *

import numpy

import inkscapeMadeEasy.inkscapeMadeEasy_Base as inkBase
import inkscapeMadeEasy.inkscapeMadeEasy_Draw as inkDraw
import inkscapeMadeEasy.inkscapeMadeEasy_Plot as inkPlot


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
        inkBase.inkscapeMadeEasy.__init__(self)

        self.arg_parser.add_argument("--tab", type=str, dest="tab", default="object")
        self.arg_parser.add_argument("--subtab_axis", type=str, dest="subtab_axis", default="object")

        self.arg_parser.add_argument("--function", type=str, dest="function", default='x*x-y*y')
        self.arg_parser.add_argument("--generalAspectFactor", type=float, dest="generalAspectFactor", default=1.0)
        self.arg_parser.add_argument("--xMin", type=float, dest="xMin", default='0.0')
        self.arg_parser.add_argument("--xMax", type=float, dest="xMax", default='0.0')
        # self.arg_parser.add_argument("--xPi", type=self.bool, dest="xPi", default=False)
        self.arg_parser.add_argument("--yMin", type=float, dest="yMin", default='0.0')
        self.arg_parser.add_argument("--yMax", type=float, dest="yMax", default='0.0')
        # self.arg_parser.add_argument("--yPi", type=self.bool, dest="yPi", default=False)

        self.arg_parser.add_argument("--xLabel", type=str, dest="xLabel", default='')
        self.arg_parser.add_argument("--xScale", type=float, dest="xScale", default='5')
        self.arg_parser.add_argument("--xTicks", type=self.bool, dest="xTicks", default=False)
        self.arg_parser.add_argument("--xTickStep", type=float, dest="xTickStep", default='1')
        self.arg_parser.add_argument("--xGrid", type=self.bool, dest="xGrid", default=True)
        # self.arg_parser.add_argument("--xExtraText", type=str, dest="xExtraText", default='')

        self.arg_parser.add_argument("--yLabel", type=str, dest="yLabel", default='')
        self.arg_parser.add_argument("--yScale", type=float, dest="yScale", default='5')
        self.arg_parser.add_argument("--yTicks", type=self.bool, dest="yTicks", default=False)
        self.arg_parser.add_argument("--yTickStep", type=float, dest="yTickStep", default='1')
        self.arg_parser.add_argument("--yGrid", type=self.bool, dest="yGrid", default=True)

        self.arg_parser.add_argument("--nSegmentsX", type=int, dest="nSegmentsX", default=10)
        self.arg_parser.add_argument("--nSegmentsY", type=int, dest="nSegmentsY", default=10)
        self.arg_parser.add_argument("--segmentAspectFactor", type=float, dest="segmentAspectFactor", default=1.0)
        self.arg_parser.add_argument("--slopeColor", type=str, dest="slopeColor", default='#FF0000')
        self.arg_parser.add_argument("--slopeColorPicker", type=str, dest="slopeColorPicker", default='0')

    def effect(self):

        so = self.options

        # sets the position to the viewport center
        position = [self.svg.namedview.center[0], self.svg.namedview.center[1]]
        position[0] = int(ceil(position[0] / 10.0)) * 10
        position[1] = int(ceil(position[1] / 10.0)) * 10

        [self.slopeColor, alpha] = inkDraw.color.parseColorPicker(so.slopeColor, so.slopeColorPicker)

        # root_layer = self.current_layer
        root_layer = self.document.getroot()
        # root_layer = self.getcurrentLayer()

        # generate xy data
        xVals = numpy.linspace(so.xMin, so.xMax, so.nSegmentsX)
        yVals = numpy.linspace(so.yMin, so.yMax, so.nSegmentsY)
        xlength = (xVals[1] - xVals[0])
        ylength = (yVals[1] - yVals[0])
        radius = min(xlength * (so.xScale / so.xTickStep), ylength * (so.yScale / so.yTickStep)) * 1.0 / 2.0

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

        inkPlot.axis.cartesian(self, slopePlot, [so.xMin, so.xMax], [so.yMin, so.yMax], position, xLabel=so.xLabel, yLabel=so.yLabel,
                               xTicks=so.xTicks, yTicks=so.yTicks, xTickStep=so.xTickStep, yTickStep=so.yTickStep, xScale=so.xScale, yScale=so.yScale,
                               xGrid=so.xGrid, yGrid=so.yGrid, forceTextSize=textSize, forceLineWidth=lineWidthAxis)

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


if __name__ == '__main__':  #
    plot = PlotSlopeField()
    plot.run()
