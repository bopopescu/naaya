// InstallPage.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2.h"
#include "InstallPage.h"
#include "CHM2Dlg.h"
#include "WizardToolz.h"
#include <Winbase.h>

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CInstallPage dialog


CInstallPage::CInstallPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CInstallPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CInstallPage)
	//}}AFX_DATA_INIT
}


void CInstallPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CInstallPage)
	DDX_Control(pDX, IDC_CHECK_START, m_chkStart);
	DDX_Control(pDX, IDC_STATIC_INFO, m_InstallInfoText);
	DDX_Control(pDX, IDC_STATIC_INSTALLATION, m_InstallationText);
	DDX_Control(pDX, IDC_PROGRESS_INSTALLATION, m_InstallationProgessText);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CInstallPage, CNewWizPage)
	//{{AFX_MSG_MAP(CInstallPage)
	ON_WM_TIMER()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CInstallPage message handlers

BOOL CInstallPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_INSTALL_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);

	m_InstallInfoText.SetWindowText(CRString(IDS_INSTALLATION_START));
	m_InstallationText.SetWindowText("");

	// disable and uncheck the Start .. checkbox
    m_chkStart.EnableWindow(FALSE);
    m_chkStart.SetCheck(FALSE);

	SetTimer(1, 500, 0);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CInstallPage::OnTimer(UINT nIDEvent) 
{
	KillTimer(1);
	
	CNewWizPage::OnTimer(nIDEvent);

	CCHM2Dlg* m_pParentDlg = ((CCHM2Dlg*)GetParent());
	CWizardData* pWizardData = m_pParentDlg->m_pWizardData;

    // Construct the path to the log file
    CString strLogFile = pWizardData->m_strPath;
    strLogFile += CRString(IDS_FILE_LOG);

    CWizardToolz toolz;
    CStringArray arrLog;

    // The installation ...
	if (StartInstallation(strLogFile))
    {
		CString strBuffer;
		strBuffer.Format(CRString(IDS_LABEL_END_INSTALL),
			pWizardData->m_strHostIPAddress,
			pWizardData->m_nZopeHTTPPort
		);
		m_InstallInfoText.SetWindowText(CRString(IDS_INSTALLATION_COMPLETE));
        m_InstallationText.SetWindowText(strBuffer);
    }
    else
    {
        // Failed to copy the files. Set a message and clean up
        m_InstallationText.SetWindowText(CRString(IDS_REMOVING_FILES));
        m_InstallInfoText.SetWindowText(CRString(IDS_DELETE_INSTALLATION_FILES));
        
        // try to delete everything from the installation folder
        // however, leave the log file - for traceback
        toolz.RecDeleteFolder(pWizardData->m_strPath + CRString(IDS_FOLDER_ZOPE));
		toolz.RecDeleteFolder(pWizardData->m_strPath + CRString(IDS_FOLDER_INSTANCE));
		toolz.RecDeleteFolder(pWizardData->m_strPath + CRString(IDS_FOLDER_BIN));
        arrLog.Add(CRString(IDS_FAIL_INSTALL));
		arrLog.Add(CRString(IDS_DELETE_INSTALLATION_FILES));

        // update labels
        m_InstallationText.SetWindowText(CRString(IDS_FAIL_INSTALL));
        m_InstallInfoText.SetWindowText("");
    }

    // Write to log
    toolz.InternalWriteToFile(strLogFile, arrLog);

	// enable buttons
    m_chkStart.EnableWindow(TRUE);
	m_chkStart.SetCheck(TRUE);
	m_pParentDlg->EnableFinish(TRUE);
}

BOOL CInstallPage::OnWizardFinish()
{
	CWizardToolz toolz;

	if (m_chkStart.GetCheck() == 1)
	{
		// start application
		CString strFile, strDirectory;
		
		strDirectory = ((CCHM2Dlg*)GetParent())->m_pWizardData->m_strPath;
		strDirectory += CRString(IDS_FOLDER_BIN);
		strFile = strDirectory;
		strFile += "\\CHM2Console.exe";

		CStringArray arrLog;
		HANDLE process = toolz.launchViaShellExecute(strFile, "", strDirectory, SW_RESTORE | SW_SHOWNORMAL);
	}
	return TRUE;
}


BOOL CInstallPage::StartInstallation(CString strLogFile)
{
    m_InstallationText.SetWindowText(CRString(IDS_LABEL_BEGIN_INSTALL));

	CWizardToolz toolz;

	// If the log file cannot be created, do not expect
	// that the installation can go on. So give a message and exit
    if (!toolz.InternalCreateFile(strLogFile))
    {
		m_InstallationText.SetWindowText(CRString(IDS_FAIL_INSTALL));
        AfxMessageBox(CRString(IDS_LABEL_NORIGHTS));
        return FALSE;
    }

    CStringArray arrLog;

	// The copy proccess
    arrLog.Add(CRString(IDS_START_COPY));
    if (!CopyNecessaryFiles(arrLog))
    {   // In case of an error, write to log and return
        arrLog.Add(CRString(IDS_FAIL_COPY));
        toolz.InternalWriteToFile(strLogFile, arrLog);
        return FALSE;
    }
    else
    {
        arrLog.Add(CRString(IDS_END_COPY));
        toolz.InternalWriteToFile(strLogFile, arrLog);
    }

	// The configuration of ini files process
    arrLog.RemoveAll();
    arrLog.Add(CRString(IDS_START_CONFIGURE));
    if (!ModifyConfigurationFiles(arrLog))
    {   // In case of an error, write to log and return
        arrLog.Add(CRString(IDS_FAIL_CONFIGURE));
        toolz.InternalWriteToFile(strLogFile, arrLog);
        return FALSE;
    }
    else
    {
        arrLog.Add(CRString(IDS_END_CONFIGURE));
        toolz.InternalWriteToFile(strLogFile, arrLog);
    }

	// Run some scripts to set stuff
    arrLog.RemoveAll();
    arrLog.Add(CRString(IDS_START_RUNSCRIPTS));
    if (!RunScripts(arrLog))
    {   // In case of an error, write to log and return
        arrLog.Add(CRString(IDS_FAIL_RUNSCRIPTS));
        toolz.InternalWriteToFile(strLogFile, arrLog);
        return FALSE;
    }
    else
    {
        arrLog.Add(CRString(IDS_END_RUNSCRIPTS));
        toolz.InternalWriteToFile(strLogFile, arrLog);
    }

	// Clean up process
    arrLog.RemoveAll();
    arrLog.Add(CRString(IDS_START_CLEANUP));
    if (!CleanUp(arrLog))
    {   // In case of an error, write to log and return
        arrLog.Add(CRString(IDS_FAIL_CLEANUP));
        toolz.InternalWriteToFile(strLogFile, arrLog);
        return FALSE;
    }
    else
    {
        arrLog.Add(CRString(IDS_END_CLEANUP));
        toolz.InternalWriteToFile(strLogFile, arrLog);
    }

    // create shortcuts
    CreateShortcuts(arrLog);

	// create registry entry
    arrLog.RemoveAll();
    arrLog.Add(CRString(IDS_START_UPDATEREGISTRY));
	UpdateRegistry(arrLog);
    arrLog.Add(CRString(IDS_END_UPDATEREGISTRY));
	toolz.InternalWriteToFile(strLogFile, arrLog);

	return TRUE;
}

BOOL CInstallPage::CopyNecessaryFiles(CStringArray& arrLog)
{
	m_InstallationText.SetWindowText(CRString(IDS_START_COPY));

	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;

    // get current folder path
    CString strCurrentDirectory;
    GetCurrentDirectory(1024, strCurrentDirectory.GetBuffer(1024));
    strCurrentDirectory.ReleaseBuffer();

    // load folder names
	CString strZopeFolder = CRString(IDS_FOLDER_ZOPE);
	CString strInstanceFolder = CRString(IDS_FOLDER_INSTANCE);
    CString strBinFolder = CRString(IDS_FOLDER_BIN);

	CWizardToolz toolz;
    toolz.m_wndProgressBar = &m_InstallationProgessText;
    toolz.m_pWizardData = pWizardData;
    
	CString strError;

    // first compute total files size
    unsigned __int64 n64TotalSize = 0;
    n64TotalSize += toolz.getFolderSize(strCurrentDirectory + strZopeFolder);
	n64TotalSize += toolz.getFolderSize(strCurrentDirectory + strInstanceFolder);
    n64TotalSize += toolz.getFolderSize(strCurrentDirectory + strBinFolder);
    pWizardData->m_n64TotalSize = n64TotalSize;
    pWizardData->m_n64PieceSize = n64TotalSize/100;

    // copy zope directory
    m_InstallationText.SetWindowText(CRString(IDS_COPY_ZOPE));
    arrLog.Add("\t" + CRString(IDS_COPY_ZOPE));
    if(toolz.InternalCreateFolder(pWizardData->m_strPath + strZopeFolder))
    {
		strError.Format(CRString(IDS_FAILED_CREATE_DIRECTORY), pWizardData->m_strPath + strZopeFolder);
        arrLog.Add(strError);
        return FALSE;
    }
    if(!toolz.RecCopyFolder(strCurrentDirectory + strZopeFolder, pWizardData->m_strPath + strZopeFolder, arrLog))
        return FALSE;

    // copy instance directory
    m_InstallationText.SetWindowText(CRString(IDS_COPY_INSTANCE));
    arrLog.Add("\t" + CRString(IDS_COPY_INSTANCE));
    if(toolz.InternalCreateFolder(pWizardData->m_strPath + strInstanceFolder))
    {
		strError.Format(CRString(IDS_FAILED_CREATE_DIRECTORY), pWizardData->m_strPath + strInstanceFolder);
        arrLog.Add(strError);
        return FALSE;
    }
    if(!toolz.RecCopyFolder(strCurrentDirectory + strInstanceFolder, pWizardData->m_strPath + strInstanceFolder, arrLog))
        return FALSE;

	// copy bin directory
    m_InstallationText.SetWindowText(CRString(IDS_COPY_BIN));
    arrLog.Add("\t" + CRString(IDS_COPY_BIN));
    if(toolz.InternalCreateFolder(pWizardData->m_strPath + strBinFolder))
    {
		strError.Format(CRString(IDS_FAILED_CREATE_DIRECTORY), pWizardData->m_strPath + strBinFolder);
        arrLog.Add(strError);
        return FALSE;
    }
    if(!toolz.RecCopyFolder(strCurrentDirectory + strBinFolder, pWizardData->m_strPath + strBinFolder, arrLog))
        return FALSE;

	// move CHM2Unins.exe from bin to application path
	CString strFilePath, strBuffer;
	strFilePath.Format("%s\\CHM2Unins.exe", pWizardData->m_strPath + strBinFolder);
	strBuffer.Format(CRString(IDS_MOVE_FILE), strFilePath, pWizardData->m_strPath + "\\CHM2Unins.exe");
    arrLog.Add(strBuffer);
	if (toolz.InternalMoveFile(pWizardData->m_strPath + strBinFolder + "\\CHM2Unins.exe", pWizardData->m_strPath + "\\CHM2Unins.exe"))
	{
		strError.Format(CRString(IDS_FAILED_MOVE_FILE), pWizardData->m_strPath + strBinFolder + "\\CHM2Unins.exe", pWizardData->m_strPath + "\\CHM2Unins.exe");
		arrLog.Add(strError);
		return FALSE;
	}

	//copy logo files
	if (pWizardData->m_strLogoPath != "")
	{
		strFilePath.Format("%s%s\\Products\\CHM2\\skel\\layout\\logo.gif", pWizardData->m_strPath, strInstanceFolder);
		strBuffer.Format(CRString(IDS_COPY_LOGO), pWizardData->m_strLogoPath, strFilePath);
		arrLog.Add(strBuffer);
		if (toolz.InternalOverwriteFile(pWizardData->m_strLogoPath, strFilePath))
		{
			strError.Format(CRString(IDS_FAILED_MOVE_FILE), pWizardData->m_strLogoPath, strFilePath);
			arrLog.Add(strError);
			return FALSE;
		}
	}

	if (pWizardData->m_strLogoBisPath != "")
	{
		strFilePath.Format("%s%s\\Products\\CHM2\\skel\\layout\\logobis.gif", pWizardData->m_strPath, strInstanceFolder);
		strBuffer.Format(CRString(IDS_COPY_LOGO), pWizardData->m_strLogoBisPath, strFilePath);
		arrLog.Add(strBuffer);
		if (toolz.InternalOverwriteFile(pWizardData->m_strLogoBisPath, strFilePath))
		{
			strError.Format(CRString(IDS_FAILED_MOVE_FILE), pWizardData->m_strLogoBisPath, strFilePath);
			arrLog.Add(strError);
			return FALSE;
		}
	}

    return TRUE;
}

BOOL CInstallPage::ModifyConfigurationFiles(CStringArray& arrLog)
{
	m_InstallationText.SetWindowText(CRString(IDS_START_CONFIGURE));

	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;

	CWizardToolz toolz;
	CString strFilePath, strContent, strBuffer;
	CString strZopeFolder = CRString(IDS_FOLDER_ZOPE);
	CString strInstanceFolder = CRString(IDS_FOLDER_INSTANCE);
	CString strBinFolder = CRString(IDS_FOLDER_BIN);

	// modify zope instance zope.conf
	strFilePath = pWizardData->m_strPath;
	strFilePath += strInstanceFolder;
	strFilePath += "\\etc\\zope.conf";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		// @@ZOPE_HTTP_PORT@@
		// @@ZOPE_FTP_PORT@@
		// @@ZOPE_WEBDAV_PORT@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath + strZopeFolder);
		strContent.Replace("@@INSTANCE_PATH@@", pWizardData->m_strPath + strInstanceFolder);
		strBuffer.Format("%d", pWizardData->m_nZopeHTTPPort);
		strContent.Replace("@@ZOPE_HTTP_PORT@@", strBuffer);
		strBuffer.Format("%d", pWizardData->m_nZopeFTPPort);
		strContent.Replace("@@ZOPE_FTP_PORT@@", strBuffer);
		strBuffer.Format("%d", pWizardData->m_nZopeWEBDAVPort);
		strContent.Replace("@@ZOPE_WEBDAV_PORT@@", strBuffer);
		
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify zope instance runzope.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strInstanceFolder;
	strFilePath += "\\bin\\runzope.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
		
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify zope instance zopeservice.py
	strFilePath = pWizardData->m_strPath;
	strFilePath += strInstanceFolder;
	strFilePath += "\\bin\\zopeservice.py";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
		
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// create zope's inituser
	strFilePath = pWizardData->m_strPath;
	strFilePath += strInstanceFolder;
	strFilePath += "\\inituser";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	strContent.Format("%s:%s", pWizardData->m_strUsername, pWizardData->m_strPassword);
	toolz.WriteFileContent(strFilePath, strContent, arrLog);

	// modify bin's chm2init.py
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\chm2init.py";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@USERNAME@@
		// @@BIN_PATH@@
		// @@PORTAL_TITLE@@
		// @@PORTAL_SUBTITLE@@
		// @@PORTAL_PUBLISHER@@
		// @@PORTAL_CONTRIBUTOR@@
		// @@PORTAL_CREATOR@@
		// @@PORTAL_RIGHTS@@
		// @@PORTAL_MAILSERVERNAME@@
		// @@PORTAL_MAILSERVERPORT@@
		// @@PORTAL_ADMINISTRATOREMAIL@@
		// @@PORTAL_DEFAULTFROMADDRESS@@
		// @@PORTAL_URL@@
		// @@PORTAL_LANGUAGES@@
		strContent.Replace("@@USERNAME@@", pWizardData->m_strUsername);
		strContent.Replace("@@BIN_PATH@@", pWizardData->m_strPath + strBinFolder);
		strContent.Replace("@@PORTAL_TITLE@@", pWizardData->m_strPortalTitle);
		strContent.Replace("@@PORTAL_SUBTITLE@@", pWizardData->m_strPortalSubtitle);
		strContent.Replace("@@PORTAL_PUBLISHER@@", pWizardData->m_strPortalPublisher);
		strContent.Replace("@@PORTAL_CONTRIBUTOR@@", pWizardData->m_strPortalContributor);
		strContent.Replace("@@PORTAL_CREATOR@@", pWizardData->m_strPortalCreator);
		strContent.Replace("@@PORTAL_RIGHTS@@", pWizardData->m_strPortalRights);
		strContent.Replace("@@PORTAL_MAILSERVERNAME@@", pWizardData->m_strMailServerName);
		strBuffer.Format("%d", pWizardData->m_nMailServerPort);
		strContent.Replace("@@PORTAL_MAILSERVERPORT@@", strBuffer);
		strContent.Replace("@@PORTAL_ADMINISTRATOREMAIL@@", pWizardData->m_strAdministratorEmail);
		strContent.Replace("@@PORTAL_DEFAULTFROMADDRESS@@", pWizardData->m_strDefaultFromAddress);
		strContent.Replace("@@PORTAL_URL@@", pWizardData->m_strPortalURL);


		CString strLanguages ;
		for (int i=0; i<pWizardData->m_arrLanguagesSel.GetSize(); i++)
		{
			int x = pWizardData->m_arrLanguagesSel.GetAt(i);
			strBuffer.Format("'%s'", pWizardData->m_arrLanguagesCodes.GetAt(x));
			strLanguages += strBuffer;
			if (i < pWizardData->m_arrLanguagesSel.GetSize()-1)
				strLanguages += ", ";
		}
		strContent.Replace("@@PORTAL_LANGUAGES@@", strLanguages);

		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify bin's chm2init.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\chm2init.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		// @@BIN_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
		strContent.Replace("@@BIN_PATH@@", pWizardData->m_strPath + strBinFolder);

		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify bin's installservice.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\installservice.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
	
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify bin's removeservice.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\removeservice.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
	
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify bin's startservice.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\startservice.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
	
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

	// modify bin's stopservice.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\stopservice.bat";
    strBuffer.Format(CRString(IDS_CONFIGURE_FILE), strFilePath);
    arrLog.Add(strBuffer);
	if (toolz.ReadFileContent(strFilePath, strContent, arrLog))
    {	// have to replace the following values:
		// @@ZOPE_PATH@@
		strContent.Replace("@@ZOPE_PATH@@", pWizardData->m_strPath);
	
		// write modified content back to file
		toolz.WriteFileContent(strFilePath, strContent, arrLog);
	}

    return TRUE;
}

BOOL CInstallPage::RunScripts(CStringArray& arrLog)
{
	m_InstallationText.SetWindowText(CRString(IDS_START_RUNSCRIPTS));

	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	CWizardToolz toolz;
	CString strBinFolder = CRString(IDS_FOLDER_BIN);
	
	CString strCommand = pWizardData->m_strPath;
	strCommand += strBinFolder;
	strCommand += "\\chm2init.bat";
	StartProgram(strCommand, "", pWizardData->m_strPath, arrLog, SW_SHOW);

	CString strBuffer;
	strBuffer.Format(CRString(IDS_EXECUTE_COMMAND), strCommand);
	arrLog.Add(strBuffer);

	return TRUE;
}

BOOL CInstallPage::CleanUp(CStringArray& arrLog)
{
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	CWizardToolz toolz;
	CString strFilePath, strBuffer;

	CString strBinFolder = CRString(IDS_FOLDER_BIN);

	// remove bin's chm2init.py
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\chm2init.py";
    strBuffer.Format(CRString(IDS_DELETE_FILE), strFilePath);
	arrLog.Add(strBuffer);
	if (toolz.InternalDeleteFile(strFilePath))
	{
        strBuffer.Format(CRString(IDS_FAILED_DELETE_FILE), strFilePath);
		arrLog.Add(strBuffer);
	}

	// remove bin's chm2init.bat
	strFilePath = pWizardData->m_strPath;
	strFilePath += strBinFolder;
	strFilePath += "\\chm2init.bat";
    strBuffer.Format(CRString(IDS_DELETE_FILE), strFilePath);
	arrLog.Add(strBuffer);
	if (toolz.InternalDeleteFile(strFilePath))
	{
        strBuffer.Format(CRString(IDS_FAILED_DELETE_FILE), strFilePath);
		arrLog.Add(strBuffer);
	}

	return TRUE;
}

BOOL CInstallPage::CreateShortcuts(CStringArray& arrLog)
{
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	CWizardToolz toolz;
	
	CString strBinFolder = CRString(IDS_FOLDER_BIN);
	CString strDirectoryPath, strLinkAddress, strLinkPath, strBuffer;
	char szBuffer[_MAX_PATH];

	arrLog.Add(CRString(IDS_LABEL_START_CREATESHORTCUTS));

	// create the folder in Start Menu -> Programs 
	::SHGetSpecialFolderPath(NULL, szBuffer, CSIDL_COMMON_PROGRAMS, 0);
	strDirectoryPath.Format("%s\\%s", szBuffer, CRString(IDS_MENU_FOLDER_NAME));
	toolz.InternalCreateFolder(strDirectoryPath);

	// create shortcut to CHM2
	strLinkAddress.Format("http://%s:%d/index_html", pWizardData->m_strHostIPAddress, pWizardData->m_nZopeHTTPPort);
	strLinkPath.Format("%s.url", CRString(IDS_SHORTCUT_CHM2_NAME));
	toolz.CreateInternetShortcut(strLinkAddress, strDirectoryPath + strLinkPath, CRString(IDS_SHORTCUT_CHM2_DESCRIPTION));
	strBuffer.Format(CRString(IDS_CREATE_SHORTCUT), CRString(IDS_SHORTCUT_CHM2_DESCRIPTION));
	arrLog.Add(strBuffer);

	// create shortcut to CHM2 console
	strBuffer.Format("%s\\CHM2Console.exe", pWizardData->m_strPath + strBinFolder);
	toolz.CreateShortcut(pWizardData->m_strPath + strBinFolder, strBuffer, strDirectoryPath + CRString(IDS_SHORTCUT_CONSOLE_NAME));
	strBuffer.Format(CRString(IDS_CREATE_SHORTCUT), CRString(IDS_SHORTCUT_CONSOLE_DESCRIPTION));
	arrLog.Add(strBuffer);

	// create shortcut to CHM2 uninstaller
	strBuffer.Format("%s\\CHM2Unins.exe", pWizardData->m_strPath);
	toolz.CreateShortcut(pWizardData->m_strPath, strBuffer, strDirectoryPath + CRString(IDS_SHORTCUT_UNINSTALL_NAME));
	strBuffer.Format(CRString(IDS_CREATE_SHORTCUT), CRString(IDS_SHORTCUT_UNINSTALL_DESCRIPTION));
	arrLog.Add(strBuffer);

	arrLog.Add(CRString(IDS_LABEL_END_CREATESHORTCUTS));

    return TRUE;
}

void CInstallPage::UpdateRegistry(CStringArray& arrLog)
{
	CWizardToolz toolz;
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;

	CString strRegString = "SOFTWARE\\" +
		CRString(IDS_REGCOMPANY) + "\\" + 
		CRString(IDS_REGAPPLICATION) + "\\";
	CString strBuffer;

	strBuffer.Format("\tRegDB Key: HKEY_LOCAL_MACHINE\\%s", strRegString);
	arrLog.Add(strBuffer);

	// set application path
	strBuffer.Format("\t\tRegDB Name: Application path");
	arrLog.Add(strBuffer);
	strBuffer.Format("\t\tRegDB Value: %s", pWizardData->m_strPath);
	arrLog.Add(strBuffer);
	toolz.CreateRegistryKey(strRegString, "Application path", pWizardData->m_strPath);

	// set zope path
	strBuffer.Format("\t\tRegDB Name: Zope path");
	arrLog.Add(strBuffer);
	strBuffer.Format("\t\tRegDB Value: %s", pWizardData->m_strPath + CRString(IDS_FOLDER_ZOPE));
	arrLog.Add(strBuffer);
	toolz.CreateRegistryKey(strRegString, "Zope path", pWizardData->m_strPath + CRString(IDS_FOLDER_ZOPE));

	// set instance path
	strBuffer.Format("\t\tRegDB Name: Instance path");
	arrLog.Add(strBuffer);
	strBuffer.Format("\t\tRegDB Value: %s", pWizardData->m_strPath + CRString(IDS_FOLDER_INSTANCE));
	arrLog.Add(strBuffer);
	toolz.CreateRegistryKey(strRegString, "Instance path", pWizardData->m_strPath + CRString(IDS_FOLDER_INSTANCE));

	// set bin path
	strBuffer.Format("\t\tRegDB Name: Bin path");
	arrLog.Add(strBuffer);
	strBuffer.Format("\t\tRegDB Value: %s", pWizardData->m_strPath + CRString(IDS_FOLDER_BIN));
	arrLog.Add(strBuffer);
	toolz.CreateRegistryKey(strRegString, "Bin path", pWizardData->m_strPath + CRString(IDS_FOLDER_BIN));
}

BOOL CInstallPage::StartProgram(CString strFile, CString strParameters, CString strDirectory, CStringArray& arrLog, int nShow)
{
	CWizardToolz toolz;
	HANDLE process = toolz.launchViaShellExecute(strFile, strParameters, strDirectory, nShow);
	if (process != NULL)
	{
		::WaitForSingleObject(process, INFINITE);
		::CloseHandle(process);
	}

	int nError = GetLastError();

    if (nError == ERROR_FILE_NOT_FOUND)
    {
        CString strBuffer = "\tThe script was not found.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_PATH_NOT_FOUND)
    {
        CString strBuffer = "\tThe path for the start script was not found.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_DDE_FAIL)
    {
        CString strBuffer = "\tThe DDE transaction failed.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_NO_ASSOCIATION)
    {
        CString strBuffer = "\tThere is no application associated with the start script.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_ACCESS_DENIED)
    {
        CString strBuffer = "\tAccess to the start script is denied.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_DLL_NOT_FOUND)
    {
        CString strBuffer = "\tOne of the library files necessary to run the start script can't be found.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_CANCELLED)
    {
        CString strBuffer = "\tThe function prompted the user for the location of the application, but the user canceled the request.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_NOT_ENOUGH_MEMORY)
    {
        CString strBuffer = "\tThere is not enough memory to start.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }
    if (nError == ERROR_SHARING_VIOLATION)
    {
        CString strBuffer = "\tA sharing violation occurred when executing the start script.";
        MessageBox(strBuffer);
        arrLog.Add(strBuffer);
    }

    if (nError != ERROR_SUCCESS)
        return FALSE;
    else
        return TRUE;
}

