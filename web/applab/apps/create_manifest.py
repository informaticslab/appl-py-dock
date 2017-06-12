from django.core.files import File
from django.conf import settings
from django.shortcuts import HttpResponse
import os, uuid

def write_manifest_send(request, app, ipa_full_url):

    tmp_directory =  'media/temp/'
    bundle_id = app.ios_project.bundle_id
    bundle_version = '{0}.{1}.{2}.{3}'.format(app.major_version,app.minor_version,app.point_version,app.build_version)
    app_title = app.ios_project.project_overview.project.title
    media_base_url = request.build_absolute_uri(settings.MEDIA_URL)
    media_base_url = media_base_url.replace('http', 'https')
    ipa_full_url = ipa_full_url.replace('http', 'https')
    base_url = media_base_url.replace('/media/', '/')

    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory)
    file_name = tmp_directory + str(uuid.uuid1())+'_manifest.plist'
    file = open(file_name, 'w')

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
    file.write('<plist version="1.0">\n')
    file.write('    <dict>\n')
    file.write('        <key>items</key>\n')
    file.write('            <array>\n')
    file.write('                <dict>\n')
    file.write('                    <key>assets</key>\n')
    file.write('                    <array>\n')
    file.write('                    <dict>\n')
    file.write('                    	<key>kind</key>\n')
    file.write('                    	<string>software-package</string>\n')
    file.write('                    	<key>url</key>\n')
    file.write('                    	<string>'+ipa_full_url+'</string>\n')
    file.write('                    </dict>\n')
    file.write('                    <dict>\n')
    file.write('                    	<key>kind</key>\n')
    file.write('                    	<string>display-image</string>\n')
    file.write('                    	<key>url</key>\n')
    file.write('                    	<string>'+media_base_url+'iiu-app-icon.57x57.png</string>\n')
    file.write('                    </dict>\n')
    file.write('                    <dict>\n')
    file.write('                    	<key>kind</key>\n')
    file.write('                    	<string>full-size-image</string>\n')
    file.write('                    	<key>url</key>\n')
    file.write('                    	<string>'+media_base_url+'iiu-app-icon.512x512.png</string>\n')
    file.write('                	</dict>\n')
    file.write('                </array>\n')
    file.write('                <key>metadata</key>\n')
    file.write('                <dict>\n')
    file.write('                    <key>bundle-identifier</key>\n')
    file.write('                    <string>'+bundle_id+'</string>\n')
    file.write('                    <key>bundle-version</key>\n')
    file.write('                    <string>'+bundle_version+'</string>\n')
    file.write('                    <key>kind</key>\n')
    file.write('                    <string>software</string>\n')
    file.write('                    <key>title</key>\n')
    file.write('                	<string>'+app_title+'</string>\n')
    file.write('				</dict>\n')
    file.write('			</dict>\n')
    file.write('		</array>\n')
    file.write('	</dict>\n')
    file.write('</plist>\n')
    file.close()


    response = HttpResponse('', status=302, content_type='application/xml')
    # response = HttpResponse(content_type='application/xml')
    response['Location'] = 'itms-services://?action=download-manifest&url='+base_url+file_name
    return response
