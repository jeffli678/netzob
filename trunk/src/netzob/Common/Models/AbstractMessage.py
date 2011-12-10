# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import uuid
import re
import glib
from netzob.Common.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractMessage :
#|     Definition of a message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class AbstractMessage():
    
    def __init__(self, id, timestamp, data, type):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.AbstractMessage.py')
        if id == None :
            self.id = uuid.uuid4()
        else :
            self.id = id 
            
        self.timestamp = timestamp
        self.data = data
        self.type = type
        self.symbol = None
        self.rightReductionFactor = 0
        self.leftReductionFactor = 0
    
    #+-----------------------------------------------------------------------+
    #| getFactory
    #|     Abstract method to retrieve the associated factory
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        self.log.error("The message class doesn't have an associated factory !")
        raise NotImplementedError("The message class doesn't have an associated factory !")
    
    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Abstract method to retrieve the properties of the message
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        self.log.error("The message class doesn't have a method 'getProperties' !")
        raise NotImplementedError("The message class doesn't have a method 'getProperties' !")
    
    #+---------------------------------------------- 
    #|`getStringData : compute a string representation
    #| of the data 
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        return str(self.data)
    
    def getReducedSize(self):
        start = 0
        end = len(self.getStringData())
        
        if self.getLeftReductionFactor() > 0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1 :
                start = start - 1
        if self.getRightReductionFactor() > 0 :
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end - start) % 2 == 1 :
                end = end + 1 
        
        if (end - start) % 2 == 1 :
            end = end + 1 
            
        return len(self.getStringData()) - (end - start)
    
    def getReducedStringData(self):        
        start = 0
        end = len(self.getStringData())
        
        if self.getLeftReductionFactor() > 0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1 :
                start = start - 1 
        if self.getRightReductionFactor() > 0 :
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end - start) % 2 == 1 :
                end = end + 1
                
                  
        return "".join(self.getStringData()[start:end]) 
    
    #+---------------------------------------------- 
    #| applyRegex: apply the current regex on the message
    #|  and return a table
    #+----------------------------------------------
    def applyRegex(self, styled=False, encoded=False):
        regex = []
        for field in self.symbol.getFields():
            regex.append(field.getRegex())
        
        compiledRegex = re.compile("".join(regex))
        data = self.getStringData()
        m = compiledRegex.match(data)
        if m == None:
            self.log.warning("The regex of the group doesn't match one of its message")
            self.log.warning("Regex: " + "".join(regex))
            self.log.warning("Message: " + data)
            return [ self.getStringData() ]
        res = []
        iCol = 0
        dynamicCol = 1
        for field in self.symbol.getFields():
            if field.getRegex().find("(") != -1: # Means this column is not static
                start = m.start(dynamicCol)
                end = m.end(dynamicCol)
                if field.getColor() == "" or field.getColor() == None:
                    color = 'blue'
                else:
                    color = field.getColor()
                if styled:
                    if encoded:
                        res.append('<span foreground="' + color + '" font_family="monospace">' + glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenType(data[start:end], field.getSelectedType())) + '</span>')
                    else:
                        res.append('<span foreground="' + color + '" font_family="monospace">' + data[start:end] + '</span>')
                else:
                    if encoded:
                        res.append(glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenType(data[start:end], field.getSelectedType())))
                    else:
                        res.append(data[start:end])
                dynamicCol += 1
            else:
                if styled:
                    if encoded:
                        res.append('<span>' + glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenType(field.getRegex(), field.getSelectedType())) + '</span>')
                    else:
                        res.append('<span>' + field.getRegex() + '</span>')
                else:
                    if encoded:
                        res.append(glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenType(field.getRegex(), field.getSelectedType())))
                    else:
                        res.append(field.getRegex())
            iCol = iCol + 1
        return res
    
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getType(self):
        return self.type
    def getData(self):
        return self.data.strip()
    def getSymbol(self):
        return self.symbol
    def getRightReductionFactor(self):
        return self.rightReductionFactor
    def getLeftReductionFactor(self):
        return self.leftReductionFactor
    def getTimestamp(self):
        return self.timestamp
    
    def setID(self, id):
        self.id = id
    def setType(self, type):
        self.type = type
    def setData(self, data):
        self.data = data
    def setSymbol(self, symbol):
        self.symbol = symbol
    def setRightReductionFactor(self, factor):
        self.rightReductionFactor = factor
        self.leftReductionFactor = 0
    def setLeftReductionFactor(self, factor):
        self.leftReductionFactor = factor
        self.rightReductionFactor = 0