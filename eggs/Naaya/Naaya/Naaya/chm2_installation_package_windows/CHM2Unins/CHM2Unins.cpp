// CHM2Unins.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "CHM2Unins.h"
#include "CHM2UninsDlg.h"

#include "UninsToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CCHM2UninsApp

BEGIN_MESSAGE_MAP(CCHM2UninsApp, CWinApp)
	//{{AFX_MSG_MAP(CCHM2UninsApp)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG
	ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CCHM2UninsApp construction

CCHM2UninsApp::CCHM2UninsApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CCHM2UninsApp object

CCHM2UninsApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CCHM2UninsApp initialization

BOOL CALLBACK CCHM2UninsApp::searcher(HWND hWnd, LPARAM lParam)
{
    DWORD result;
    LRESULT ok = ::SendMessageTimeout(hWnd,
                                      UWM_ARE_YOU_ME,
                                      0, 0, 
                                      SMTO_BLOCK |
                                      SMTO_ABORTIFHUNG,
                                      200,
                                      &result);
    if(ok == 0)
       return TRUE; // ignore this and continue
    if(result == UWM_ARE_YOU_ME)
    { /* found it */
        HWND * target = (HWND *)lParam;
        *target = hWnd;
        return FALSE; // stop search
    } /* found it */
    return TRUE; // continue search
}

BOOL CCHM2UninsApp::InitInstance()
{
	AfxEnableControlContainer();

	// Standard initialization
	// If you are not using these features and wish to reduce the size
	//  of your final executable, you should remove from the following
	//  the specific initialization routines you do not need.

#ifdef _AFXDLL
	Enable3dControls();			// Call this when using MFC in a shared DLL
#else
	Enable3dControlsStatic();	// Call this when linking to MFC statically
#endif

	// first check that current user is an Administrator on this machine
	BOOL bIsAdministrator = CUninsToolz().RunningAsAdministrator();

	if (bIsAdministrator)
	{
		bool AlreadyRunning;
		CString strMutexName;
		strMutexName.Format("%s-088FA840-B10D-11D3-BC36-006067709674", AfxGetAppName());

		HANDLE hMutexOneInstance = ::CreateMutex( NULL, FALSE, strMutexName);

		AlreadyRunning = ( ::GetLastError() == ERROR_ALREADY_EXISTS || 
						   ::GetLastError() == ERROR_ACCESS_DENIED);

		if ( AlreadyRunning )
		{ /* kill this */
			HWND hOther = NULL;
			EnumWindows(searcher, (LPARAM)&hOther);

			if ( hOther != NULL )
			{ /* pop up */
				::SetForegroundWindow( hOther );

				if ( IsIconic( hOther ) )
				{ /* restore */
					::ShowWindow( hOther, SW_RESTORE );
				} /* restore */
			} /* pop up */

			return FALSE; // terminates the creation
		} /* kill this */

		CCHM2UninsDlg dlg;
		m_pMainWnd = &dlg;
		int nResponse = dlg.DoModal();
		if (nResponse == IDOK)
		{
			// TODO: Place code here to handle when the dialog is
			//  dismissed with OK
		}
		else if (nResponse == IDCANCEL)
		{
			// TODO: Place code here to handle when the dialog is
			//  dismissed with Cancel
		}
	}
	else
	{
		MessageBox(NULL, CRString(IDS_ABORT_UNINSTALL), CRString(IDS_BOX_CAPTION), MB_OK | MB_ICONWARNING);
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.
	return FALSE;
}
