#-----------------------------------------------------------------------------
# ply: lex.py
#
# Author: David M. Beazley (beazley@cs.uchicago.edu)
#         Department of Computer Science
#         University of Chicago
#         Chicago, IL  60637
#
# Copyright (C) 2001, David M. Beazley
#
# $Header: /cvsroot/textindexng/TextIndexNG/parsers/FrenchQueryParser/lex.py,v 1.1 2005/02/21 18:14:44 tarek-ziade Exp $
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 
# See the file COPYING for a complete copy of the LGPL.
#
# 
# This module automatically constructs a lexical analysis module from regular
# expression rules defined in a user-defined module.  The idea is essentially the same
# as that used in John Aycock's Spark framework, but the implementation works
# at the module level rather than requiring the use of classes.
#
# This module tries to provide an interface that is closely modeled after
# the traditional lex interface in Unix.  It also differs from Spark
# in that:
#
#   -  It provides more extensive error checking and reporting if
#      the user supplies a set of regular expressions that can't
#      be compiled or if there is any other kind of a problem in
#      the specification.
#
#   -  The interface is geared towards LALR(1) and LR(1) parser
#      generators.  That is tokens are generated one at a time
#      rather than being generated in advanced all in one step.
#
# There are a few limitations of this module
#
#   -  The module interface makes it somewhat awkward to support more
#      than one lexer at a time.  Although somewhat inelegant from a
#      design perspective, this is rarely a practical concern for
#      most compiler projects.
#
#   -  The lexer requires that the entire input text be read into
#      a string before scanning.  I suppose that most machines have
#      enough memory to make this a minor issues, but it makes
#      the lexer somewhat difficult to use in interactive sessions
#      or with streaming data.
#
#-----------------------------------------------------------------------------

r"""
lex.py

This module builds lex-like scanners based on regular expression rules.
To use the module, simply write a collection of regular expression rules
and actions like this:

# lexer.py
import lex

# Define a list of valid tokens
tokens = (
    'IDENTIFIER', 'NUMBER', 'PLUS', 'MINUS'
    )

# Define tokens as functions
def t_IDENTIFIER(t):
    r' ([a-zA-Z_](\w|_)* '
    return t

def t_NUMBER(t):
    r' \d+ '
    return t

# Some simple tokens with no actions
t_PLUS = r'\+'
t_MINUS = r'-'

# Initialize the lexer
lex.lex()

The tokens list is required and contains a complete list of all valid
token types that the lexer is allowed to produce.  Token types are
restricted to be valid identifiers.  This means that 'MINUS' is a valid
token type whereas '-' is not.

Rules are defined by writing a function with a name of the form
t_rulename.  Each rule must accept a single argument which is
a token object generated by the lexer. This token has the following
attributes:

    t.type   = type string of the token.  This is initially set to the
               name of the rule without the leading t_
    t.value  = The value of the lexeme.
    t.lineno = The value of the line number where the token was encountered
    
For example, the t_NUMBER() rule above might be called with the following:
    
    t.type  = 'NUMBER'
    t.value = '42'
    t.lineno = 3

Each rule returns the token object it would like to supply to the
parser.  In most cases, the token t is returned with few, if any
modifications.  To discard a token for things like whitespace or
comments, simply return nothing.  For instance:

def t_whitespace(t):
    r' \s+ '
    pass

For faster lexing, you can also define this in terms of the ignore set like this:

t_ignore = ' \t'

The characters in this string are ignored by the lexer. Use of this feature can speed
up parsing significantly since scanning will immediately proceed to the next token.

lex requires that the token returned by each rule has an attribute
t.type.  Other than this, rules are free to return any kind of token
object that they wish and may construct a new type of token object
from the attributes of t (provided the new object has the required
type attribute).

If illegal characters are encountered, the scanner executes the
function t_error(t) where t is a token representing the rest of the
string that hasn't been matched.  If this function isn't defined, a
LexError exception is raised.  The .text attribute of this exception
object contains the part of the string that wasn't matched.

The t.skip(n) method can be used to skip ahead n characters in the
input stream.  This is usually only used in the error handling rule.
For instance, the following rule would print an error message and
continue:

def t_error(t):
    print "Illegal character in input %s" % t.value[0]
    t.skip(1)

Of course, a nice scanner might wish to skip more than one character
if the input looks very corrupted.

The lex module defines a t.lineno attribute on each token that can be used
to track the current line number in the input.  The value of this
variable is not modified by lex so it is up to your lexer module
to correctly update its value depending on the lexical properties
of the input language.  To do this, you might write rules such as
the following:

def t_newline(t):
    r' \n+ '
    t.lineno += t.value.count("\n")

To initialize your lexer so that it can be used, simply call the lex.lex()
function in your rule file.  If there are any errors in your
specification, warning messages or an exception will be generated to
alert you to the problem.

(dave: this needs to be rewritten)
To use the newly constructed lexer from another module, simply do
this:

    import lex
    import lexer
    plex.input("position = initial + rate*60")

    while 1:
        token = plex.token()       # Get a token
        if not token: break        # No more tokens
        ... do whatever ...

Assuming that the module 'lexer' has initialized plex as shown
above, parsing modules can safely import 'plex' without having
to import the rule file or any additional imformation about the
scanner you have defined.
"""    

# -----------------------------------------------------------------------------


__version__ = "1.0"

import re, types, sys

# Exception thrown when invalid token encountered and no default
class LexError(Exception):
    def __init__(self,message,s):
         self.args = (message,)
         self.text = s

# Token class
class LexToken:
    def __str__(self):
        return "LexToken(%s,%r,%d)" % (self.type,self.value,self.lineno)
    def __repr__(self):
        return str(self)
    def skip(self,n):
        try:
            self._skipn += n
        except AttributeError:
            self._skipn = n

# -----------------------------------------------------------------------------
# Lexer class
#
#    input()          -  Store a new string in the lexer
#    token()          -  Get the next token
# -----------------------------------------------------------------------------

class Lexer:
    def __init__(self):
        self.lexre = None           # Main regular expression
        self.lexdata = None         # Actual input data (as a string)
        self.lexpos = 0             # Current position in input text
        self.lexlen = 0             # Length of the input text
        self.lexindexfunc = [ ]     # Reverse mapping of groups to functions and types
        self.lexerrorf = None       # Error rule (if any)
        self.lextokens = None       # List of valid tokens
        self.lexignore = None       # Ignored characters
        self.lineno = 1             # Current line number
        self.debug = 0              # Debugging mode
        self.optimize = 0           # Optimized mode
        self.token = self.errtoken

        self.hack = LexToken()
        
    # ------------------------------------------------------------
    # input() - Push a new string into the lexer
    # ------------------------------------------------------------
    def input(self,s):
        if not type(s) in (types.StringType,types.UnicodeType):
            raise ValueError, "Expected a string or unicode"
        self.lexdata = s
        self.lexpos = 0
        self.lexlen = len(s)
        self.token = self.realtoken

        # Change the token routine to point to realtoken()
        global token
        if token == self.errtoken:
            token = self.token

    # ------------------------------------------------------------
    # errtoken() - Return error if token is called with no data
    # ------------------------------------------------------------
    def errtoken(self):
        raise RuntimeError, "No input string given with input()"
    
    # ------------------------------------------------------------
    # token() - Return the next token from the Lexer
    #
    # Note: This function has been carefully implemented to be as fast
    # as possible.  Don't make changes unless you really know what
    # you are doing
    # ------------------------------------------------------------
    def realtoken(self):
        # Make local copies of frequently referenced attributes
        lexpos    = self.lexpos
        lexlen    = self.lexlen
        lexignore = self.lexignore
        lexdata   = self.lexdata

        while lexpos < lexlen:
            # This code provides some short-circuit code for whitespace, tabs, and other ignored characters
            if lexdata[lexpos] in lexignore:
                lexpos += 1
                continue

            # Look for a regular expression match
            m = self.lexre.match(lexdata,lexpos)
            if m:
                i = m.lastindex
                lexpos = m.end()
                tok = LexToken()
                tok.value = m.group()
                tok.lineno = self.lineno
                func,tok.type = self.lexindexfunc[i]
                if not func:
                    self.lexpos = lexpos
                    return tok
                
                # If token is processed by a function, call it
                self.lexpos = lexpos
                tok.lexer = self
                newtok = func(tok)
                self.lineno = tok.lineno     # Update line number
                
                # Every function must return a token, if nothing, we just move to next token
                if not newtok: continue
                
                # Verify type of the token.  If not in the token map, raise an error
                if not self.optimize:
                    if not self.lextokens.has_key(newtok.type):
                        raise LexError, ("%s:%d. Rule '%s' returned an unknown token type '%s'" % (
                            func.func_code.co_filename, func.func_code.co_firstlineno,
                            func.__name__, newtok.type),lexdata[lexpos:])

                return newtok

            # No match. Call t_error() if defined.
            if self.lexerrorf:
                tok = LexToken()
                tok.value = self.lexdata[lexpos:]
                tok.lineno = self.lineno
                tok.type = "error"
                tok.lexer = self
                oldpos = lexpos
                newtok = self.lexerrorf(tok)
                lexpos += getattr(tok,"_skipn",0)
                if oldpos == lexpos:
                    # Error method didn't change text position at all. This is an error.
                    self.lexpos = lexpos
                    raise LexError, ("Scanning error. Illegal character '%s'" % (lexdata[lexpos]), lexdata[lexpos:])
                if not newtok: continue
                self.lexpos = lexpos
                return newtok

            self.lexpos = lexpos
            raise LexError, ("No match found", lexdata[lexpos:])

        # No more input data
        self.lexpos = lexpos + 1
        return None

        
# -----------------------------------------------------------------------------
# validate_file()
#
# This checks to see if there are duplicated t_rulename() functions or strings
# in the parser input file.  This is done using a simple regular expression
# match on each line in the filename.
# -----------------------------------------------------------------------------

def validate_file(filename):
    import os.path
    base,ext = os.path.splitext(filename)
    if ext != '.py': return 1        # No idea what the file is. Return OK

    try:
        f = open(filename)
        lines = f.readlines()
        f.close()
    except IOError:
        return 1                       # Oh well

    fre = re.compile(r'\s*def\s+(t_[a-zA-Z_0-9]*)\(')
    sre = re.compile(r'\s*(t_[a-zA-Z_0-9]*)\s*=')
    counthash = { }
    linen = 1
    noerror = 1
    for l in lines:
        m = fre.match(l)
        if not m:
            m = sre.match(l)
        if m:
            name = m.group(1)
            prev = counthash.get(name)
            if not prev:
                counthash[name] = linen
            else:
                print "%s:%d: Rule %s redefined. Previously defined on line %d" % (filename,linen,name,prev)
                noerror = 0
        linen += 1
    return noerror

        
# -----------------------------------------------------------------------------
# lex(module)
#
# Build all of the regular expression rules from definitions in the supplied module
# -----------------------------------------------------------------------------
def lex(module=None,debug=0,optimize=0):
    ldict = None
    regex = ""
    error = 0
    files = { }
    lexer = Lexer()
    lexer.debug = debug
    lexer.optimize = optimize
    
    if module:
        if not isinstance(module, types.ModuleType):
            raise ValueError,"Expected a module"
        
        ldict = module.__dict__
        
    else:
        # No module given.  We might be able to get information from the caller.
        try:
            raise RuntimeError
        except RuntimeError:
            e,b,t = sys.exc_info()
            f = t.tb_frame
            f = f.f_back           # Walk out to our calling function
            ldict = f.f_globals    # Grab its globals dictionary
        
    # Get the tokens map
    tokens = ldict.get("tokens",None)
    if not tokens:
        raise SyntaxError,"lex: module does not define 'tokens'"
    if not (isinstance(tokens,types.ListType) or isinstance(tokens,types.TupleType)):
        raise SyntaxError,"lex: tokens must be a list or tuple."

    # Build a dictionary of valid token names
    lexer.lextokens = { }
    if not optimize:

        # Utility function for verifying tokens
        def is_identifier(s):
            for c in s:
                if not (c.isalnum() or c == '_'): return 0
            return 1
        
        for n in tokens:
            if not is_identifier(n):
                print "lex: Bad token name '%s'" % n
                error = 1
            if lexer.lextokens.has_key(n):
                print "lex: Warning. Token '%s' multiply defined." % n
            lexer.lextokens[n] = None
    else:
        for n in tokens: lexer.lextokens[n] = None
        

    if debug:
        print "lex: tokens = '%s'" % lexer.lextokens.keys()

    # Get a list of symbols with the t_ prefix
    tsymbols = [f for f in ldict.keys() if f[:2] == 't_']

    # Now build up a list of functions and a list of strings
    fsymbols = [ ]
    ssymbols = [ ]
    for f in tsymbols:
        if isinstance(ldict[f],types.FunctionType):
            fsymbols.append(ldict[f])
        elif isinstance(ldict[f],types.StringType):
            ssymbols.append((f,ldict[f]))
        else:
            print "lex: %s not defined as a function or string" % f
            error = 1
            
    # Sort the functions by line number
    fsymbols.sort(lambda x,y: cmp(x.func_code.co_firstlineno,y.func_code.co_firstlineno))

    # Sort the strings by regular expression length
    ssymbols.sort(lambda x,y: (len(x[1]) < len(y[1])) - (len(x[1]) > len(y[1])))
    
    # Check for non-empty symbols
    if len(fsymbols) == 0 and len(ssymbols) == 0:
        raise SyntaxError,"lex: no rules of the form t_rulename are defined."

    # Add all of the rules defined with actions first
    for f in fsymbols:
        
        line = f.func_code.co_firstlineno
        file = f.func_code.co_filename
        files[file] = None

        if not optimize:
            if f.func_code.co_argcount > 1:
                print "%s:%d. Rule '%s' has too many arguments." % (file,line,f.__name__)
                error = 1
                continue

            if f.func_code.co_argcount < 1:
                print "%s:%d. Rule '%s' requires an argument." % (file,line,f.__name__)
                error = 1
                continue

            if f.__name__ == 't_ignore':
                print "%s:%d. Rule '%s' must be defined as a string." % (file,line,f.__name__)
                error = 1
                continue
        
        if f.__name__ == 't_error':
            lexer.lexerrorf = f
            continue

        if f.__doc__:
            if not optimize:
                try:
                    c = re.compile(f.__doc__, re.VERBOSE|re.UNICODE|re.LOCALE)
                except re.error,e:
                    print "%s:%d. Invalid regular expression for rule '%s'. %s" % (file,line,f.__name__,e)
                    error = 1
                    continue

                if debug:
                    print "lex: Adding rule %s -> '%s'" % (f.__name__,f.__doc__)

            # Okay. The regular expression seemed okay.  Let's append it to the main regular
            # expression we're building
  
            if (regex): regex += "|"
            regex += "(?P<%s>%s)" % (f.__name__,f.__doc__)
        else:
            print "%s:%d. No regular expression defined for rule '%s'" % (file,line,f.__name__)

    # Now add all of the simple rules
    for name,r in ssymbols:

        if name == 't_ignore':
            lexer.lexignore = r
            continue
        
        if not optimize:
            if name == 't_error':
                raise SyntaxError,"lex: Rule 't_error' must be defined as a function"
                error = 1
                continue
        
            if not lexer.lextokens.has_key(name[2:]):
                print "lex: Rule '%s' defined for an unspecified token %s." % (name,name[2:])
                error = 1
                continue
            try:
                c = re.compile(r,re.VERBOSE|re.UNICODE|re.LOCALE)
            except re.error,e:
                print "lex: Invalid regular expression for rule '%s'. %s" % (name,e)
                error = 1
                continue
            if debug:
                print "lex: Adding rule %s -> '%s'" % (name,r)
                
        if regex: regex += "|"
        regex += "(?P<%s>%s)" % (name,r)

    if not optimize:
        for f in files.keys():
            if not validate_file(f):
                error = 1
    try:
        if debug:
            print "lex: regex = '%s'" % regex
        lexer.lexre = re.compile(regex, re.VERBOSE|re.UNICODE|re.LOCALE)

        # Build the index to function map for the matching engine
        lexer.lexindexfunc = [ None ] * (max(lexer.lexre.groupindex.values())+1)
        for f,i in lexer.lexre.groupindex.items():
            handle = ldict[f]
            if isinstance(handle,types.FunctionType):
                lexer.lexindexfunc[i] = (handle,handle.__name__[2:])
            else:
                # If rule was specified as a string, we build an anonymous
                # callback function to carry out the action
                lexer.lexindexfunc[i] = (None,f[2:])

    except re.error,e:
        print "lex: Fatal error. Unable to compile regular expression rules. %s" % e
        error = 1
    if error:
        raise SyntaxError,"lex: Unable to build lexer."
    if not lexer.lexerrorf:
        print "lex: Warning. no t_error rule is defined."

    if not lexer.lexignore: lexer.lexignore = ""
    
    # Create global versions of the token() and input() functions
    global token, input
    token = lexer.token
    input = lexer.input
    
    return lexer

# -----------------------------------------------------------------------------
# run()
#
# This runs the lexer as a main program
# -----------------------------------------------------------------------------

def runmain(lexer=None,data=None):
    if not data:
        try:
            filename = sys.argv[1]
            f = open(filename)
            data = f.read()
            f.close()
        except IndexError:
            print "Reading from standard input (type EOF to end):"
            data = sys.stdin.read()

    if lexer:
        _input = lexer.input
    else:
        _input = input
    _input(data)
    if lexer:
        _token = lexer.token
    else:
        _token = token
        
    while 1:
        tok = _token()
        if not tok: break
        print "(%s,'%s',%d)" % (tok.type, tok.value, tok.lineno)
        
    


