# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from google.appengine.api import conversion


class PdfConversionError(Exception):
    pass


def convertPdf(data,
               imageWidth=1000,
               dstContentType='image/png',
               fileName='dummyFileName',
               pageNumber=None):
    """
    Pass in the raw binary PDF data. Returns the raw binary image data
    result after rasterization.
    """
    asset = conversion.Asset("application/pdf", data, fileName)
    requestKwargs = {'image_width': imageWidth}
    if pageNumber is not None:
        requestKwargs.update({'first_page': pageNumber, 'last_page': pageNumber})
    conversionObj = conversion.Conversion(asset, dstContentType, **requestKwargs)

    result = conversion.convert(conversionObj)
    if result.assets:
        return result.assets[0].data
    else:
        raise PdfConversionError('%s [code %s]' % (result.error_text, result.error_code))
