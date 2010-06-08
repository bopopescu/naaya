# Example code:

BODY = """<span tal:replace="python:request.RESPONSE.setHeader('content-type', 'text/html; charset=UTF-8')"/>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<tal:block define="	lang python:request.get('lang', here.gl_get_selected_language());
					skin_path python:here.getLayoutTool().getSkinFilesPath();
					ctrl python:request.get('ctrl', '');
					tab python:request.get('tab', 'them');
					theme_id python:request.get('theme_id', '')">

	<html xmlns="http://www.w3.org/1999/xhtml" tal:attributes="xml:lang lang; lang lang;">
	<head tal:define="skin_files_path python:here.getLayoutTool().getSkinFilesPath()">
		<title tal:content="here/title_or_id" />
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<link rel="home" tal:attributes="href python:request['BASE0']" title="Home" />
		<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${skin_files_path}/style_common" />
	</head>
<body onload="this.focus();">
<div class="pick_pop_up">
<h1 i18n:translate="">Image insertion</h1>

<a tal:attributes="href string:${here/absolute_url}/gallerybox_html">Pick an image from photo gallery</a><br />
<a tal:attributes="href string:${here/absolute_url}/graphicsgallerybox_html">Pick an image from graphics gallery</a>
<p i18n:translate="">This window allows you to <strong>upload</strong> images and <strong>insert</strong> them in your text.</p>

<form method="post" action="process_image_upload" enctype="multipart/form-data"  style="margin-bottom:1.2em;">
<a name="upload"></a>
<strong i18n:translate="">Upload an image</strong><br /><br />
<input type="file" name="file" />
<input type="submit" value="Upload" />
</form>

	<a name="insert"></a>
	<strong i18n:translate="">Insert an image</strong>
<tal:block  define="images here/getUploadedImages">
<tal:block condition="images">
<p i18n:translate="">Click on an image to insert it in your text. Also you can select images for deletion.</p>
<form method="post" action="process_delete">
<input tal:condition="python:len(images)>5" type="submit" value="Delete selected images" i18n:attributes="value" />
<ul style="list-style:none;">
	<li tal:repeat="item images">
		<input type="checkbox" name="ids" tal:attributes="value item/id" />
		<img tal:attributes="src item/absolute_url;
				alt item/title_or_id;
				onclick string:window.opener.CreateImage('${item/absolute_url}');; window.close();;"
			border="0" width="32" style="cursor: pointer;" />
	</li>
</ul>
<input type="submit" value="Delete selected images" i18n:attributes="value" />
</form>
</tal:block>
<tal:block condition="not:images">
<p i18n:translate="">No images available. In order to insert an image in your text please <strong>upload</strong> one first.</p>
</tal:block>
</tal:block>
<hr style="border: 1px solid #f0f0f0; background-color:white;" />
<form>
<input type="button" value="Close window" onclick="javascript:window.close();" i18n:attributes="value" />
</form>
</div>
</body>
</html>
</tal:block>"""

update_only = ['burkina', 'tunisie', 'comores', 'burundi', 'niger', 'madagascar', 'maroc', 'comifac2', 'ethiopia', 'test', 'rca', 'rdcongo', 'ghana', 'algerie', 'zambia', 'mali', 'basissite', 'formation_chm_madagascar', 'togo', 'mauritanie', 'civoire', 'formation_chm_reg_maroc', 'mauritius', 'maroc/tanger', 'formchm15', 'benin']

for portal in container.get_portals(exclude=True):
    if portal.id in update_only:
        portal.portal_forms.epoz_toolbox.pt_edit(text=BODY, content_type='text/html')

print 'DONE - epoz_toolbox'
return printed
