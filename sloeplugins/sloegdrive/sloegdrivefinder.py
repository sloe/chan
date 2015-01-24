
import sloelib

from .sloegdrivesession import SloeGDriveSession

class SloeGDriveFinder(object):
    def __init__(self):
        self.session_r = None


    def get_session_r(self):
        if not self.session_r:
            self.session_r = SloeGDriveSession("r")

        return self.session_r()


    def ids_to_records(self, file_ids):
        records = []
        for file_id in file_ids:
            req = dict(
                fields='alternateLink,fileExtension,fileSize,id,md5Checksum,mimeType,openWithLinks,permissions(id,kind),title,videoMediaMetadata,webContentLink',
                fileId=file_id
            )
            response = self.get_session_r().files().get(**req).execute()
            records.append(response)
        return records


    def find_ids(self, find_str, exact):
        elements = find_str.split('/')

        child_ids = ['root']
        if exact:
            operator = '='
        else:
            operator = 'contains'

        for element in elements:
            new_child_ids = []
            for child_id in child_ids:
                escaped_element = element.replace("'", "\\'")
                req = dict(
                    fields='items/id',
                    folderId=child_id,
                    q="title %s '%s'" % (operator, escaped_element)
                )
                response = self.get_session_r().children().list(**req).execute()
                items = response.get('items', None)

                new_child_ids += [item['id'] for item in items]
            child_ids = new_child_ids

        return child_ids


    def find(self, find_str, exact):
        ids = self.find_ids(find_str, exact)
        return self.ids_to_records(ids)
