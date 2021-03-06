# -*- coding: UTF-8 -*-
# Copyright (C) 2007  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Wrapper around Zope versions."""


try:
    import zope.annotation
except ImportError:
    # Zope 2.9
    zope_version = '2.9'
    from TAL.TALInterpreter import interpolate
else:
    # Zope 2.10
    zope_version = '2.10'
    from zope.i18n import interpolate
