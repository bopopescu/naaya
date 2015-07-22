<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!--
	main html banner
	-->
	<xsl:template name="banner">

		<table width="100%">

			<!-- title -->
			<div id="container" style="">
				<div id="toolribbon">
					<div id="left_topnav">
					    <ul>
						<li><a href="http://www.ew.eea.europa.eu" title="EnviroWindows">EnviroWindows</a></li>
						<li><a href="http://www.eea.europa.eu" id="eealink">EEA</a></li>
						<li><a href="http://www.eionet.europa.eu">Eionet</a></li>
						<li><a href="http://www.gmes.info">GMES</a></li>
					    </ul>
					</div>
				</div>
				<div id="header">
					<a href="http://gmes.info/"><img class="leftfl" src="http://gisc.ew.eea.europa.eu/portal_layout/logo_en.gif" title="GMES" alt="GMES"></img></a>
					<a href="http://www.eea.europa.eu/"><img class="rightfl" src="http://gisc.ew.eea.europa.eu/portal_layout/envirowindows/EW-skin-13/logo-eea"></img></a>
					<a href="http://cordis.europa.eu/fp7/home_en.html"><img class="rightfl" src="http://gisc.ew.eea.europa.eu/portal_layout/envirowindows/EW-skin-13/logo-fp7"></img></a>
					<div class="page_title">GISC Catalogue</div>
				</div>
				<div id="menunav">
				</div>
				<div id="breadcrumbtrail">
					<a title="EnviroWindows" href="http://ew.eea.europa.eu">EW</a>
					 »
					<a href="http://gisc.ew.eea.europa.eu/" title="Home">Home</a>
					 »
					<a href="http://gisc.ew.eea.europa.eu/geonetwork/" title="Geonetwork">Geonetwork</a>
				</div>
			</div>

			<!-- buttons -->
			<tr class="banner">
				<td class="banner-menu" width="380px">
					<a class="banner" href="{/root/gui/locService}/main.home"><xsl:value-of select="/root/gui/strings/home"/></a>
					|
<!--		//FIXME			<xsl:if test="string(/root/gui/results)!=''">
						<xsl:choose>
							<xsl:when test="/root/gui/reqService='main.present'">
								<font class="banner-active"><xsl:value-of select="/root/gui/strings/result"/></font>
							</xsl:when>
							<xsl:otherwise>
								<a class="banner" href="{/root/gui/locService}/main.present"><xsl:value-of select="/root/gui/strings/result"/></a>
							</xsl:otherwise>
						</xsl:choose>
						|
					</xsl:if> -->
					<xsl:if test="string(/root/gui/session/userId)!=''">
						<xsl:choose>
							<xsl:when test="/root/gui/reqService='admin'">
								<font class="banner-active"><xsl:value-of select="/root/gui/strings/admin"/></font>
							</xsl:when>
							<xsl:otherwise>
								<a class="banner" href="{/root/gui/locService}/admin"><xsl:value-of select="/root/gui/strings/admin"/></a>
							</xsl:otherwise>
						</xsl:choose>
						|
					</xsl:if>
					<xsl:choose>
						<xsl:when test="/root/gui/reqService='feedback'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/contactUs"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/locService}/feedback"><xsl:value-of select="/root/gui/strings/contactUs"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/reqService='links'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/links"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/locService}/links"><xsl:value-of select="/root/gui/strings/links"/></a>
						</xsl:otherwise>
					</xsl:choose>
					<xsl:if test="string(/root/gui/session/userId)='' and
								     string(/root/gui/env/userSelfRegistration/enable)='true'">
					|
						<xsl:choose>
							<xsl:when test="/root/gui/reqService='user.register.get'">
								<font class="banner-active"><xsl:value-of select="/root/gui/strings/register"/></font>
							</xsl:when>
							<xsl:otherwise>
								<a class="banner" href="{/root/gui/locService}/user.register.get"><xsl:value-of select="/root/gui/strings/register"/></a>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:if>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/reqService='about'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/about"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/locService}/about"><xsl:value-of select="/root/gui/strings/about"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
<!--					<xsl:choose>
						<xsl:when test="/root/gui/reqService='help'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/help"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/locService}/help"><xsl:value-of select="/root/gui/strings/help"/></a>
						</xsl:otherwise>
					</xsl:choose> -->

					<!-- Help section to be displayed according to GUI language -->
					<xsl:choose>
						<xsl:when test="/root/gui/language='fr'">
							<a class="banner" href="{/root/gui/url}/docs/fra/" target="_blank"><xsl:value-of select="/root/gui/strings/help"/></a>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/url}/docs/eng/" target="_blank"><xsl:value-of select="/root/gui/strings/help"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
				</td>
				<td align="right" class="banner-menu" width="610px">
					<xsl:choose>
						<xsl:when test="/root/gui/language='cn'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/cn"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/cn/main.home"><xsl:value-of select="/root/gui/strings/cn"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='en'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/en"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/en/main.home"><xsl:value-of select="/root/gui/strings/en"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='es'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/es"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/es/main.home"><xsl:value-of select="/root/gui/strings/es"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='pt'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/pt"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/pt/main.home"><xsl:value-of select="/root/gui/strings/pt"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='fr'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/fr"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/fr/main.home"><xsl:value-of select="/root/gui/strings/fr"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='ru'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/ru"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/ru/main.home"><xsl:value-of select="/root/gui/strings/ru"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='de'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/de"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/de/main.home"><xsl:value-of select="/root/gui/strings/de"/></a>
						</xsl:otherwise>
					</xsl:choose>
					|
					<xsl:choose>
						<xsl:when test="/root/gui/language='nl'">
							<font class="banner-active"><xsl:value-of select="/root/gui/strings/nl"/></font>
						</xsl:when>
						<xsl:otherwise>
							<a class="banner" href="{/root/gui/service}/nl/main.home"><xsl:value-of select="/root/gui/strings/nl"/></a>
						</xsl:otherwise>
					</xsl:choose>
				</td>
			</tr>

			<!-- FIXME: should also contain links to last results and metadata -->

			<!-- login -->
			<tr class="banner">
				<td class="banner-login" align="right" width="380px">
					<!-- FIXME
					<button class="banner" onclick="goSubmit('{/root/gui/service}/es/main.present')">Last search results (11-20 of 73)</button>
					<a class="banner" href="{/root/gui/service}/es/main.present">Last search results (11-20 of 73)<xsl:value-of select="/root/gui/strings/results"/></a>
					-->
				</td>
				<xsl:choose>
					<xsl:when test="string(/root/gui/session/userId)!=''">
						<td align="right" class="banner-login">
							<form name="logout" action="{/root/gui/locService}/user.logout" method="post">
								<xsl:value-of select="/root/gui/strings/user"/>
								<xsl:text>: </xsl:text>
								<xsl:value-of select="/root/gui/session/name"/>
								<xsl:text> </xsl:text>
								<xsl:value-of select="/root/gui/session/surname"/>
								<xsl:text> </xsl:text>
								<button class="banner" onclick="goSubmit('logout')"><xsl:value-of select="/root/gui/strings/logout"/></button>
							</form>
						</td>
					</xsl:when>
					<xsl:otherwise>
						<td align="right" class="banner-login">
							<form name="login" action="{/root/gui/locService}/user.login" method="post">
								<xsl:if test="string(/root/gui/env/shib/use)='true'">
									<a class="banner" href="{/root/gui/env/shib/path}">
										<xsl:value-of select="/root/gui/strings/shibLogin"/>
									</a>
									|
								</xsl:if>
								<input type="submit" style="display: none;" />
								<xsl:value-of select="/root/gui/strings/username"/>
								<input class="banner" type="text" id="username" name="username" size="10" onkeypress="return entSub('login')"/>
								<xsl:value-of select="/root/gui/strings/password"/>
								<input class="banner" type="password" id="password" name="password" size="10" onkeypress="return entSub('login')"/>
								<button class="banner" onclick="goSubmit('login')"><xsl:value-of select="/root/gui/strings/login"/></button>
							</form>
						</td>
					</xsl:otherwise>
				</xsl:choose>
			</tr>
		</table>
	</xsl:template>

	<!--
	main html banner in a popup window
	-->
	<xsl:template name="bannerPopup">

		<table width="100%">

			<!-- title -->
			<!-- TODO : Mutualize with main banner template -->
			<tr class="banner">
				<td class="banner">
					<img src="{/root/gui/url}/images/header-left.jpg" alt="GeoNetwork opensource" align="top" />
				</td>
				<td align="right" class="banner">
					<img src="{/root/gui/url}/images/header-right.gif" alt="World picture" align="top" />
				</td>
			</tr>

			<!-- buttons -->
			<tr class="banner">
				<td class="banner-menu" colspan="2">
				</td>
			</tr>

			<tr class="banner">
				<td class="banner-login" colspan="2">
				</td>
			</tr>
		</table>
	</xsl:template>


</xsl:stylesheet>

