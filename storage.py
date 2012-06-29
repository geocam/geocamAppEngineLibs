from __future__ import with_statement
from django.core.files.storage import Storage
from google.appengine.api import files, urlfetch
from google.appengine.ext import blobstore
import os
import logging

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

