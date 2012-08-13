
from __future__ import with_statement
import os
import logging

from django.core.files.storage import Storage

from google.appengine.api import files, urlfetch
from google.appengine.ext import blobstore

class GCSStorage(Storage):
    def __init__(self, options=None):
        if not options:
            from django.conf import settings # settings can't be imported on module load, since this object is instantiated in siteSettings.py
            options = getattr(settings, 'GCS_OPTIONS')
        self.bucket = options['bucket']

    def _gcs_path(self, name):
        return  "/gs/"+self.bucket+"/"+name
        
    def _gcs_url(self, name):
        return "http://%s.commondatastorage.googleapis.com/%s" % ( self.bucket, name )

    def _head_request(self, name):
        return urlfetch.fetch(
            url = self._gcs_url(name),
            method=urlfetch.HEAD,
        )

    def _blobkey(self, name):
        return blobstore.create_gs_key(self._gcs_path(name))

    ##
    # Required by the Storage interface
    ##

    def _open(self, name, mode='r'):
        if mode not in ('r','a'):
            raise NotImplementedError
        objectname = self._gcs_path(name)
        return files.open(objectname, mode)

    def _save(self, name, content):
        objectname = self._gcs_path(name)
        writable_name = files.gs.create(objectname, mime_type='application/vnd.google-earth.kml+xml', acl="public-read")
        with files.open(writable_name, 'a') as fp:
            fp.write(content.read())
        files.finalize(writable_name)
        logging.debug("_save wrote %s " % objectname )
        return name

    def delete(self, name):
        blob_key = self._blobkey(name)
        blobstore.delete(blob_key)
        raise NotImplementedError

    def exists(self, name):
        logging.debug("GCSStorage.exists() was called.")
        blob_key = self._blobkey(name)
        if blobstore.get(blob_key):
            logging.info("blobstore key %s exists" % str(blob_key))
            return True
        else:
            logging.info("blobstore key %s does not exist" % str(blob_key))
            return False

    def listdir(self, dirname):
        raise NotImplementedError

    def size(self, name):
        blob_key = self._blobkey(name)
        blobinfo = blobstore.get(blob_key)
        if blobinfo:
            return blobinfo.size
        else:
            raise Exception("object does not exist at %s" % name)

    def url(self, name):
        return self._gcs_url(name)



    ##
    # Optional:
    # anything else listed in https://docs.djangoproject.com/en/1.3/ref/files/storage/#django.core.files.storage.Storage
    ##


MIME_TYPE_LOOKUP = {
    '.kml': 'application/vnd.google-earth.kml+xml',
    '.kmz': 'application/vnd.google-earth.kmz+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
}

class BlobReaderWrapper(blobstore.BlobReader):
    """
    This shim is needed to make a BlobReader look more like a django.core.files.File.
    """
    
    def __init__(self, reader):
        self.reader = reader

    def __getattr__(self, *args, **kwargs):
        """
        Proxy all calls not defined here to the real BlobReader object.
        """
        return self.reader.__getattr__(*args, **kwargs)

    def open(self, mode=None):
        pass  # BlobReader is already open, duh


class BlobStorage(Storage):
    def __init__(self):
        super(BlobStorage, self).__init__()

    @classmethod
    def _getBlob(cls, name):
        return blobstore.BlobInfo.get(blobstore.BlobKey(name))

    def _open(self, name, mode):
        if mode not in ('r', 'rb'):
            raise NotImplementedError()
        return self._getBlob(name).open()

    def _save(self, name, content):
        ext = os.path.splitext(name)[1]
        mime_type = MIME_TYPE_LOOKUP.get(ext, 'application/octet-stream')

        # Create the file
        file_name = files.blobstore.create(mime_type=mime_type)

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
            if not isinstance(content, basestring):
                # in case content is a file-like object
                content = content.read()
            f.write(content)

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)

        # Get the file's blob key
        blob_key = files.blobstore.get_blob_key(file_name)

        logging.info("_save wrote %s with content type %s" % (blob_key, mime_type))

        return str(blob_key)

    def delete(self, name):
        blobstore.BlobInfo.delete(self._getBlob(name))

    def exists(self, name):
        logging.debug("BlobStorage.exists() was called.")
        result = (self._getBlob(name) is not None)
        logging.info("blobstore key %s exists = %s" % (name, result))
        return result

    def listdir(self, dirname):
        raise NotImplementedError()

    def size(self, name):
        blob = self._getBlob(name)
        if blob:
            return blob.size
        else:
            raise KeyError("blob does not exist at %s" % name)

    def url(self, name):
        raise NotImplementedError()

    ##
    # Optional:
    # anything else listed in https://docs.djangoproject.com/en/1.3/ref/files/storage/#django.core.files.storage.Storage
    ##

def test():
    bs = BlobStorage()
    key = bs._save('foo.jpg', 'content')
    print 'file exists = %s' % bs.exists(key)
    f = bs._open(key)
    print f.read()
    f.close()
    bs.delete(key)
    print 'file exists = %s' % bs.exists(key)
    print bs.url(key)
