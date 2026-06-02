#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
"""Record of phased-in incompatible language changes.

Each line is of the form:

    FeatureName = "_Feature(" OptionalRelease "," MandatoryRelease ","
                              CompilerFlag ")"

where, normally, OptionalRelease < MandatoryRelease, and both are 5-tuples
of the same form as sys.version_info:

    (PY_MAJOR_VERSION, # the 2 in 2.1.0a3; an int
     PY_MINOR_VERSION, # the 1; an int
     PY_MICRO_VERSION, # the 0; an int
     PY_RELEASE_LEVEL, # "alpha", "beta", "candidate" or "final"; string
     PY_RELEASE_SERIAL # the 3; an int
    )

OptionalRelease records the first release in which

    from __future__ import FeatureName

was accepted.

In the case of MandatoryReleases that have not yet occurred,
MandatoryRelease predicts the release in which the feature will become part
of the language.

Else MandatoryRelease records when the feature became part of the language;
in releases at or after that, modules no longer need

    from __future__ import FeatureName

to use the feature in question, but may continue to use such imports.

MandatoryRelease may also be None, meaning that a planned feature got
dropped or that the release version is undetermined.

Instances of class _Feature have two corresponding methods,
.getOptionalRelease() and .getMandatoryRelease().

CompilerFlag is the (bitfield) flag that should be passed in the fourth
argument to the builtin function compile() to enable the feature in
dynamically compiled code.  This flag is stored in the .compiler_flag
attribute on _Future instances.  These values must match the appropriate
#defines of CO_xxx flags in Include/cpython/compile.h.

No feature line is ever to be deleted from this file.
"""

all_feature_names = [
    "nested_scopes",
    "generators",
    "division",
    "absolute_import",
    "with_statement",
    "print_function",
    "unicode_literals",
    "barry_as_FLUFL",
    "generator_stop",
    "annotations",
]

__all__ = ["all_feature_names"] + all_feature_names

# The CO_xxx symbols are defined here under the same names defined in
# code.h and used by compile.h, so that an editor search will find them here.
# However, they're not exported in __all__, because they don't really belong to
# this module.
CO_NESTED = 0x0010                      # nested_scopes
CO_GENERATOR_ALLOWED = 0                # generators (obsolete, was 0x1000)
CO_FUTURE_DIVISION = 0x20000            # division
CO_FUTURE_ABSOLUTE_IMPORT = 0x40000     # perform absolute imports by default
CO_FUTURE_WITH_STATEMENT = 0x80000      # with statement
CO_FUTURE_PRINT_FUNCTION = 0x100000     # print function
CO_FUTURE_UNICODE_LITERALS = 0x200000   # unicode string literals
CO_FUTURE_BARRY_AS_BDFL = 0x400000
CO_FUTURE_GENERATOR_STOP = 0x800000     # StopIteration becomes RuntimeError in generators
CO_FUTURE_ANNOTATIONS = 0x1000000       # annotations become strings at runtime


class _Feature:

    def __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    def getOptionalRelease(self):
        """Return first release in which this feature was recognized.

        This is a 5-tuple, of the same form as sys.version_info.
        """
        return self.optional

    def getMandatoryRelease(self):
        """Return release in which this feature will become mandatory.

        This is a 5-tuple, of the same form as sys.version_info, or, if
        the feature was dropped, or the release date is undetermined, is None.
        """
        return self.mandatory

    def __repr__(self):
        return "_Feature" + repr((self.optional,
                                  self.mandatory,
                                  self.compiler_flag))


nested_scopes = _Feature((2, 1, 0, "beta",  1),
                         (2, 2, 0, "alpha", 0),
                         CO_NESTED)

generators = _Feature((2, 2, 0, "alpha", 1),
                      (2, 3, 0, "final", 0),
                      CO_GENERATOR_ALLOWED)

division = _Feature((2, 2, 0, "alpha", 2),
                    (3, 0, 0, "alpha", 0),
                    CO_FUTURE_DIVISION)

absolute_import = _Feature((2, 5, 0, "alpha", 1),
                           (3, 0, 0, "alpha", 0),
                           CO_FUTURE_ABSOLUTE_IMPORT)

with_statement = _Feature((2, 5, 0, "alpha", 1),
                          (2, 6, 0, "alpha", 0),
                          CO_FUTURE_WITH_STATEMENT)

print_function = _Feature((2, 6, 0, "alpha", 2),
                          (3, 0, 0, "alpha", 0),
                          CO_FUTURE_PRINT_FUNCTION)

unicode_literals = _Feature((2, 6, 0, "alpha", 2),
                            (3, 0, 0, "alpha", 0),
                            CO_FUTURE_UNICODE_LITERALS)

barry_as_FLUFL = _Feature((3, 1, 0, "alpha", 2),
                          (4, 0, 0, "alpha", 0),
                          CO_FUTURE_BARRY_AS_BDFL)

generator_stop = _Feature((3, 5, 0, "beta", 1),
                          (3, 7, 0, "alpha", 0),
                          CO_FUTURE_GENERATOR_STOP)

annotations = _Feature((3, 7, 0, "beta", 1),
                       None,
                       CO_FUTURE_ANNOTATIONS)


#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
import sys
import struct

# pylint: disable=import-error, no-name-in-module
if sys.version_info < (3, 0):
    __base = object
else:
    from collections.abc import Sequence

    __base = Sequence


# pylint: disable=too-many-public-methods,useless-object-inheritance
class GXByteBuffer(__base):
    """
    Byte array class is used to save received bytes.
    """
    #   print("mst")
    __HEX_ARRAY = "0123456789ABCDEFGH"
    __NIBBLE = 4
    __LOW_BYTE_PART = 0x0F
    __ARRAY_CAPACITY = 10

    def __init__(self, value=None):
        """
        Constructor.
        value: Buffer or capacity.
        """
        self._data = bytearray()
        self.__size = 0
        self.__position = 0
        if isinstance(value, (bytearray, bytes)):
            self.setCapacity(len(value))
            self.set(value)
        elif isinstance(value, GXByteBuffer):
            self.setCapacity(value.size - value.position)
            self.set(value)
        elif isinstance(value, int):
            self.setCapacity(value)
        elif isinstance(value, str):
            self.setHexString(value)
        else:
            self.setCapacity(0)

    def clear(self):
        """
        Clear buffer but do not release memory.
        """
        self.position = 0
        self.size = 0

    #
    #      Buffer capacity.
    #
    # Buffer capacity.
    #
    def getCapacity(self):
        if not self._data:
            return 0
        return len(self._data)

    #
    #      Allocate new size for the array in bytes.
    #
    #      @param capacity
    #                 Buffer capacity.
    #
    def setCapacity(self, capacity):
        if capacity == 0:
            self._data = bytearray()
            self.__size = 0
            self.__position = 0
        else:
            if not self._data:
                self._data = bytearray(capacity)
            else:
                tmp = self._data
                self._data = bytearray(capacity)
                if self.size < capacity:
                    self._data[0 : self.size] = tmp
                else:
                    self._data[0:capacity] = self._data
                    self.__size = capacity

    capacity = property(getCapacity, setCapacity)
    """Buffer capacity."""

    def getPosition(self):
        return self.__position

    def setPosition(self, value):
        if value < 0 or value > len(self):
            raise ValueError("position")
        self.__position = value

    position = property(getPosition, setPosition)
    """Buffer position."""

    def getSize(self):
        return self.__size

    def setsize(self, value):
        if value < 0 or value > self.capacity:
            raise ValueError("size")
        self.__size = value
        if self.__position > self.__size:
            self.__position = self.__size

    size = property(getSize, setsize)
    """Buffer size."""

    def __len__(self):
        """Buffer size."""
        return self.__size

    def __getitem__(self, i):
        return self._data[i]

    def available(self):
        """Amount of non read bytes in the buffer."""
        return self.size - self.position

    #
    # Get buffer data as byte array.
    #
    def array(self):
        return self.subArray(0, self.size)

    #
    #      Returns sub array from byte buffer.
    #
    #      @param index
    #                 Start index.
    #      @param count
    #                 Byte count.
    # Sub array.
    #
    def subArray(self, index, count):
        if count != 0:
            tmp = bytearray(count)
            tmp[0:count] = self._data[index : index + count]
            return tmp
        return bytearray(0)

    #
    #      Move content from source to destination.
    #
    #      @param srcPos
    #                 Source position.
    #      @param destPos
    #                 Destination position.
    #      @param count
    #                 Item count.
    #
    def move(self, srcPos, destPos, count):
        if count < 0:
            raise ValueError("count")
        if count != 0:
            self._data[destPos : destPos + count] = self._data[srcPos : srcPos + count]
            self.size = destPos + count
            if self.position > self.size:
                self.position = self.size

    #
    #      Remove handled bytes.  This can be used in debugging to remove
    #      handled
    #      bytes.
    #
    def trim(self):
        if self.size == self.position:
            self.size = 0
        else:
            self.move(self.position, 0, self.size - self.position)
        self.position = 0

    #
    #      Push the given byte into this buffer at the current position, and
    #      then
    #      increments the position.
    #
    #      @param item
    #                 The byte to be added.
    #
    def setUInt8(self, item, index=None):
        if index is None:
            self.setUInt8(item, self.size)
            self.size += 1
        else:
            if index >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            self._data[index] = item

    #
    #      Push the given byte into this buffer at the current position, and
    #      then
    #      increments the position.
    #
    #      @param item
    #                 The byte to be added.
    #
    def setInt8(self, item, index=None):
        self.setUInt8(item & 0xFF, index)

    def setUInt16(self, item, index=None):
        if index is None:
            self.setUInt16(item, self.size)
            self.size += 2
        else:
            if index + 2 >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            self._data[index] = int(((item >> 8) & 0xFF))
            self._data[index + 1] = int((item & 0xFF))

    def setUInt32(self, item, index=None):
        if index is None:
            self.setUInt32(item, self.size)
            self.size += 4
        else:
            if index + 4 >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            self._data[index] = int(((item >> 24) & 0xFF))
            self._data[index + 1] = int(((item >> 16) & 0xFF))
            self._data[index + 2] = int(((item >> 8) & 0xFF))
            self._data[index + 3] = int((item & 0xFF))

    def setUInt64(self, item, index=None):
        if index is None:
            self.setUInt64(item, self.size)
            self.size += 8
        else:
            if index + 8 >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            self._data[self.size] = int(((item >> 56) & 0xFF))
            self._data[self.size + 1] = int(((item >> 48) & 0xFF))
            self._data[self.size + 2] = int(((item >> 40) & 0xFF))
            self._data[self.size + 3] = int(((item >> 32) & 0xFF))
            self._data[self.size + 4] = int(((item >> 24) & 0xFF))
            self._data[self.size + 5] = int(((item >> 16) & 0xFF))
            self._data[self.size + 6] = int(((item >> 8) & 0xFF))
            self._data[self.size + 7] = int((item & 0xFF))

    def setFloat(self, value, index=None):
        if index is None:
            self.setFloat(value, self.size)
            self.size += 4
        else:
            if index + 4 >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            tmp = struct.pack("f", value)
            self._data[self.size] = tmp[3]
            self._data[self.size + 1] = tmp[2]
            self._data[self.size + 2] = tmp[1]
            self._data[self.size + 3] = tmp[0]

    def setDouble(self, value, index=None):
        if index is None:
            self.setDouble(value, self.size)
            self.size += 8
        else:
            if index + 8 >= self.capacity:
                self.capacity = index + self.__ARRAY_CAPACITY
            tmp = struct.pack("d", value)
            # Swap bytes.
            self._data[self.size] = tmp[7]
            self._data[self.size + 1] = tmp[6]
            self._data[self.size + 2] = tmp[5]
            self._data[self.size + 3] = tmp[4]
            self._data[self.size + 4] = tmp[3]
            self._data[self.size + 5] = tmp[2]
            self._data[self.size + 6] = tmp[1]
            self._data[self.size + 7] = tmp[0]

    def getUInt8(self, index=None):
        if index is None:
            index = self.position
            value = self._data[index] & 0xFF
            value = value % 2**8
            self.position += 1
            return value
        if index >= self.size:
            raise ValueError("getUInt8")
        value = self._data[index] & 0xFF
        value = value % 2**8
        return value

    def getInt8(self, index=None):
        if index is None:
            index = self.position
            value = self._data[index]
            value = (value + 2**7) % 2**8 - 2**7
            self.position += 1
            return value
        if index >= self.size:
            raise ValueError("getInt8")
        value = self._data[index]
        value = (value + 2**7) % 2**8 - 2**7
        return value

    def getUInt16(self, index=None):
        if index is None:
            index = self.position
            value = ((self._data[index] & 0xFF) << 8) | (self._data[index + 1] & 0xFF)
            value = value % 2**16
            self.position += 2
            return value
        if index + 2 > self.size:
            raise ValueError("getUInt16")
        value = ((self._data[index] & 0xFF) << 8) | (self._data[index + 1] & 0xFF)
        value = value % 2**16
        return value

    def getInt16(self):
        return (self.getUInt16() + 2**15) % 2**16 - 2**15

    def getInt32(self, index=None):
        if index is None:
            index = self.position
            if index + 4 > self.size:
                raise ValueError("getInt32")
            value = (
                (self._data[index] & 0xFF) << 24
                | (self._data[index + 1] & 0xFF) << 16
                | (self._data[index + 2] & 0xFF) << 8
                | (self._data[index + 3] & 0xFF)
            )
            value = (value + 2**31) % 2**32 - 2**31
            self.position += 4
            return value

        if index + 4 > self.size:
            raise ValueError("getInt32")
        value = (
            (self._data[index] & 0xFF) << 24
            | (self._data[index + 1] & 0xFF) << 16
            | (self._data[index + 2] & 0xFF) << 8
            | (self._data[index + 3] & 0xFF)
        )
        value = (value + 2**31) % 2**32 - 2**31
        return value

    def getUInt32(self, index=None):
        if index is None:
            index = self.position
            self.position += 4
        if index + 4 > self.size:
            raise ValueError("getUInt32")
        value = self._data[index] & 0xFF
        value = value << 24
        value |= (self._data[index + 1] & 0xFF) << 16
        value |= (self._data[index + 2] & 0xFF) << 8
        value |= self._data[index + 3] & 0xFF
        value = value % 2**32
        return value

    def getFloat(self):
        tmp = bytearray(4)
        self.get(tmp)
        # Swap bytes.
        tmp2 = tmp[0]
        tmp[0] = tmp[3]
        tmp[3] = tmp2
        tmp2 = tmp[1]
        tmp[1] = tmp[2]
        tmp[2] = tmp2
        return struct.unpack("f", tmp)[0]

    def getDouble(self):
        tmp = bytearray(8)
        self.get(tmp)
        # Swap bytes.
        tmp2 = tmp[0]
        tmp[0] = tmp[7]
        tmp[7] = tmp2
        tmp2 = tmp[1]
        tmp[1] = tmp[6]
        tmp[6] = tmp2
        tmp2 = tmp[2]
        tmp[2] = tmp[5]
        tmp[5] = tmp2
        tmp2 = tmp[3]
        tmp[3] = tmp[4]
        tmp[4] = tmp2
        return struct.unpack("d", tmp)[0]

    def getInt64(self, index=None):
        if index is None:
            index = self.position
            self.position += 8
        value = ((self._data[index] & 0xFF)) << 56
        value |= ((self._data[index + 1] & 0xFF)) << 48
        value |= ((self._data[index + 2] & 0xFF)) << 40
        value |= ((self._data[index + 3] & 0xFF)) << 32
        value |= ((self._data[index + 4] & 0xFF)) << 24
        value |= (self._data[index + 5] & 0xFF) << 16
        value |= (self._data[index + 6] & 0xFF) << 8
        value |= self._data[index + 7] & 0xFF
        value = (value + 2**63) % 2**64 - 2**63
        return value

    def getUInt64(self, index=None):
        value = self.getInt64(index)
        return value % 2**64

    #
    #      Check is byte buffer ASCII string.
    #
    #      @param value
    #                 Byte array.
    # Is ASCII string.
    #
    @classmethod
    def isAsciiString(cls, value):
        # pylint: disable=too-many-boolean-expressions
        if value:
            for it in value:
                if (
                    (it < 32 or it > 127)
                    and it != "\r"
                    and it != "\n"
                    and it != "\t"
                    and it != 0
                ):
                    return False
        return True

    def getString(self, index, count):
        if index is None and count is None:
            tmp = self._data[0 : self.size]
            if self.isAsciiString(tmp):
                str_ = tmp.decode("utf-8").rstrip("\x00")
            else:
                str_ = self.hex(tmp)
            self.position += count
            return str_

        if index + count > self.size:
            raise ValueError("getString")
        tmp = self._data[index : index + count]
        if self.isAsciiString(tmp):
            return tmp.decode("utf-8").rstrip("\x00")
        return self.hex(tmp)

    def set(self, value, index=None, count=None):
        # pylint: disable=protected-access
        if isinstance(value, str):
            value = value.encode()
        if value:
            if index is None:
                if isinstance(value, GXByteBuffer):
                    index = value.position
                else:
                    index = 0
            if count is None:
                count = len(value) - index
            if isinstance(value, GXByteBuffer):
                self.set(value._data, index, count)
                value.position = index + count
            elif value and count != 0:
                if self.size + count > self.capacity:
                    self.capacity = self.size + count + self.__ARRAY_CAPACITY
                self._data[self.size : self.size + count] = value[index : index + count]
                self.size += count

    def get(self, target):
        len1 = len(target)
        if self.size - self.position < len1:
            raise ValueError("get")
        index = 0
        for index in range(0, len1):
            target[index] = self._data[self.position]
            self.position = self.position + 1

    #
    #      Compares, whether two given arrays are similar starting from current
    #      position.
    #
    #      @param arr
    #                 Array to compare.
    # True, if arrays are similar.  False, if the arrays differ.
    #
    def compare(self, arr):
        len1 = len(arr)
        if not arr or (self.size - self.position < len1):
            return False
        bytes_ = bytearray(len1)
        self.get(bytes_)
        ret = arr == bytes_
        if not ret:
            self.position -= len1
        return ret

    #
    #      Reverses the order of the given array.
    #
    def reverse(self):
        first = self.position
        last = self.size - 1
        tmp = int()
        while last > first:
            tmp = self._data[last]
            self._data[last] = self._data[first]
            self._data[first] = tmp
            last -= 1
            first += 1

    #
    #      Push the given hex string as byte array into this buffer at the
    #      current
    #      position, and then increments the position.
    #
    #      @param value
    #                 Byte array to add.
    #      @param index
    #                 Byte index.
    #      @param count
    #                 Byte count.
    #
    def setHexString(self, value, index=0, count=None):
        tmp = self.hexToBytes(value)
        if count is None:
            count = len(tmp)
        self.set(tmp, index, count)

    def __str__(self):
        return self.hex(self._data, True, 0, self.size)

    #
    #      Get remaining data.
    #
    # Remaining data as byte array.
    #
    def remaining(self):
        return self.subArray(self.position, self.size - self.position)

    #
    #      Get remaining data as a hex string.
    #
    #      @param addSpace
    #                 Add space between bytes.
    # Remaining data as a hex string.
    #
    def remainingHexString(self, addSpace=True):
        return self.hex(self._data, addSpace, self.position, self.size - self.position)

    #
    #      Get data as hex string.
    #
    #      @param addSpace
    #                 Add space between bytes.
    #      @param index
    #                 Byte index.
    #      @param count
    #                 Byte count.
    # Data as hex string.
    #
    def toHex(self, addSpace=True, index=0, count=None):
        if count is None:
            count = len(self) - index
        return self.hex(self._data, addSpace, index, count)

    # Convert char hex value to byte value.
    @classmethod
    def ___getValue(cls, c):
        # Id char.
        if c.islower():
            c = c.upper()
        pos = GXByteBuffer.__HEX_ARRAY.find(c)
        if pos == -1:
            raise Exception("Invalid hex string")
        return pos

    @classmethod
    def hexToBytes(cls, value):
        """Convert string to byte array.
        value: Hex string.
        Returns byte array.
        """
        buff = bytearray()
        if value:
            lastValue = -1
            for ch in value:
                if ch != " ":
                    if lastValue == -1:
                        lastValue = GXByteBuffer.___getValue(ch)
                    elif lastValue != -1:
                        buff.append(
                            lastValue << GXByteBuffer.__NIBBLE
                            | GXByteBuffer.___getValue(ch)
                        )
                        lastValue = -1
                elif lastValue != -1:
                    buff.append(GXByteBuffer.___getValue(ch))
                    lastValue = -1
        return buff

    @classmethod
    def hex(cls, value, addSpace=True, index=0, count=None):
        """
        Convert byte array to hex string.
        """
        # Return empty string if array is empty.
        if not value:
            return ""
        hexChars = ""
        # Python 2.7 handles bytes as a string array. It's changed to bytearray.
        if sys.version_info < (3, 0) and not isinstance(value, bytearray):
            value = bytearray(value)
        if count is None:
            count = len(value)
        for it in value[index : index + count]:
            hexChars += GXByteBuffer.__HEX_ARRAY[it >> GXByteBuffer.__NIBBLE]
            hexChars += GXByteBuffer.__HEX_ARRAY[it & GXByteBuffer.__LOW_BYTE_PART]
            if addSpace:
                hexChars += " "
        return hexChars.strip()


#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#pylint: disable=broad-except
try:
    from enum import IntEnum
    class GXIntEnum(IntEnum):
        """Enum class."""
except Exception:
    class GXIntEnum(int):
        """Enum class."""

class Security(GXIntEnum):
    """Used security model."""
    #pylint: disable=too-few-public-methods
    # Transport security is not used.
    NONE = 0
    # Authentication security is used.
    AUTHENTICATION = 0x10
    # Encryption security is used.
    ENCRYPTION = 0x20
    # Authentication and Encryption security are used.
    AUTHENTICATION_ENCRYPTION = 0x30

# pylint: disable=too-many-public-methods,too-many-instance-attributes,too-many-arguments
class GXDLMSChipperingStream:
    """
    Implements GMAC.  This class is based to this doc:
    http://csrc.nist.gov/publications/nistpubs/800-38D/SP-800-38D.pdf
    """

    #  Consts.
    BLOCK_SIZE = 16
    TAG_SIZE = 0x10
    IV = [0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6]

     #schedule Vector (powers of x).
    R_CON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,\
        0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc,\
        0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef,\
        0xc5, 0x91)

    #S box
    S_BOX = (0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,\
        0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76, 0xCA, 0x82,\
        0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF,\
        0x9C, 0xA4, 0x72, 0xC0, 0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F,\
        0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,\
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12,\
        0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75, 0x09, 0x83, 0x2C, 0x1A,\
        0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3,\
        0x2F, 0x84, 0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B,\
        0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF, 0xD0, 0xEF,\
        0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F,\
        0x50, 0x3C, 0x9F, 0xA8, 0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D,\
        0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,\
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7,\
        0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73, 0x60, 0x81, 0x4F, 0xDC,\
        0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E,\
        0x0B, 0xDB, 0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C,\
        0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79, 0xE7, 0xC8,\
        0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA,\
        0x65, 0x7A, 0xAE, 0x08, 0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6,\
        0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,\
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35,\
        0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E, 0xE1, 0xF8, 0x98, 0x11,\
        0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55,\
        0x28, 0xDF, 0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68,\
        0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16)

     #Inverse sbox
    S_BOX_REVERSED = (0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5,\
        0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb, 0x7c,\
        0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43,\
        0x44, 0xc4, 0xde, 0xe9, 0xcb, 0x54, 0x7b, 0x94, 0x32, 0xa6,\
        0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3,\
        0x4e, 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76,\
        0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25, 0x72, 0xf8, 0xf6,\
        0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d,\
        0x65, 0xb6, 0x92, 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9,\
        0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84, 0x90,\
        0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58,\
        0x05, 0xb8, 0xb3, 0x45, 0x06, 0xd0, 0x2c, 0x1e, 0x8f, 0xca,\
        0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a,\
        0x6b, 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97,\
        0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73, 0x96, 0xac, 0x74,\
        0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c,\
        0x75, 0xdf, 0x6e, 0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5,\
        0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b, 0xfc,\
        0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0,\
        0xfe, 0x78, 0xcd, 0x5a, 0xf4, 0x1f, 0xdd, 0xa8, 0x33, 0x88,\
        0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec,\
        0x5f, 0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d,\
        0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef, 0xa0, 0xe0, 0x3b,\
        0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83,\
        0x53, 0x99, 0x61, 0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6,\
        0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d)

     #Rijndael (AES) Encryption fast table.
    AES = (0xa56363c6, 0x847c7cf8, 0x997777ee,\
        0x8d7b7bf6, 0x0df2f2ff, 0xbd6b6bd6, 0xb16f6fde, 0x54c5c591,\
        0x50303060, 0x03010102, 0xa96767ce, 0x7d2b2b56, 0x19fefee7,\
        0x62d7d7b5, 0xe6abab4d, 0x9a7676ec, 0x45caca8f, 0x9d82821f,\
        0x40c9c989, 0x877d7dfa, 0x15fafaef, 0xeb5959b2, 0xc947478e,\
        0x0bf0f0fb, 0xecadad41, 0x67d4d4b3, 0xfda2a25f, 0xeaafaf45,\
        0xbf9c9c23, 0xf7a4a453, 0x967272e4, 0x5bc0c09b, 0xc2b7b775,\
        0x1cfdfde1, 0xae93933d, 0x6a26264c, 0x5a36366c, 0x413f3f7e,\
        0x02f7f7f5, 0x4fcccc83, 0x5c343468, 0xf4a5a551, 0x34e5e5d1,\
        0x08f1f1f9, 0x937171e2, 0x73d8d8ab, 0x53313162, 0x3f15152a,\
        0x0c040408, 0x52c7c795, 0x65232346, 0x5ec3c39d, 0x28181830,\
        0xa1969637, 0x0f05050a, 0xb59a9a2f, 0x0907070e, 0x36121224,\
        0x9b80801b, 0x3de2e2df, 0x26ebebcd, 0x6927274e, 0xcdb2b27f,\
        0x9f7575ea, 0x1b090912, 0x9e83831d, 0x742c2c58, 0x2e1a1a34,\
        0x2d1b1b36, 0xb26e6edc, 0xee5a5ab4, 0xfba0a05b, 0xf65252a4,\
        0x4d3b3b76, 0x61d6d6b7, 0xceb3b37d, 0x7b292952, 0x3ee3e3dd,\
        0x712f2f5e, 0x97848413, 0xf55353a6, 0x68d1d1b9, 0x00000000,\
        0x2cededc1, 0x60202040, 0x1ffcfce3, 0xc8b1b179, 0xed5b5bb6,\
        0xbe6a6ad4, 0x46cbcb8d, 0xd9bebe67, 0x4b393972, 0xde4a4a94,\
        0xd44c4c98, 0xe85858b0, 0x4acfcf85, 0x6bd0d0bb, 0x2aefefc5,\
        0xe5aaaa4f, 0x16fbfbed, 0xc5434386, 0xd74d4d9a, 0x55333366,\
        0x94858511, 0xcf45458a, 0x10f9f9e9, 0x06020204, 0x817f7ffe,\
        0xf05050a0, 0x443c3c78, 0xba9f9f25, 0xe3a8a84b, 0xf35151a2,\
        0xfea3a35d, 0xc0404080, 0x8a8f8f05, 0xad92923f, 0xbc9d9d21,\
        0x48383870, 0x04f5f5f1, 0xdfbcbc63, 0xc1b6b677, 0x75dadaaf,\
        0x63212142, 0x30101020, 0x1affffe5, 0x0ef3f3fd, 0x6dd2d2bf,\
        0x4ccdcd81, 0x140c0c18, 0x35131326, 0x2fececc3, 0xe15f5fbe,\
        0xa2979735, 0xcc444488, 0x3917172e, 0x57c4c493, 0xf2a7a755,\
        0x827e7efc, 0x473d3d7a, 0xac6464c8, 0xe75d5dba, 0x2b191932,\
        0x957373e6, 0xa06060c0, 0x98818119, 0xd14f4f9e, 0x7fdcdca3,\
        0x66222244, 0x7e2a2a54, 0xab90903b, 0x8388880b, 0xca46468c,\
        0x29eeeec7, 0xd3b8b86b, 0x3c141428, 0x79dedea7, 0xe25e5ebc,\
        0x1d0b0b16, 0x76dbdbad, 0x3be0e0db, 0x56323264, 0x4e3a3a74,\
        0x1e0a0a14, 0xdb494992, 0x0a06060c, 0x6c242448, 0xe45c5cb8,\
        0x5dc2c29f, 0x6ed3d3bd, 0xefacac43, 0xa66262c4, 0xa8919139,\
        0xa4959531, 0x37e4e4d3, 0x8b7979f2, 0x32e7e7d5, 0x43c8c88b,\
        0x5937376e, 0xb76d6dda, 0x8c8d8d01, 0x64d5d5b1, 0xd24e4e9c,\
        0xe0a9a949, 0xb46c6cd8, 0xfa5656ac, 0x07f4f4f3, 0x25eaeacf,\
        0xaf6565ca, 0x8e7a7af4, 0xe9aeae47, 0x18080810, 0xd5baba6f,\
        0x887878f0, 0x6f25254a, 0x722e2e5c, 0x241c1c38, 0xf1a6a657,\
        0xc7b4b473, 0x51c6c697, 0x23e8e8cb, 0x7cdddda1, 0x9c7474e8,\
        0x211f1f3e, 0xdd4b4b96, 0xdcbdbd61, 0x868b8b0d, 0x858a8a0f,\
        0x907070e0, 0x423e3e7c, 0xc4b5b571, 0xaa6666cc, 0xd8484890,\
        0x05030306, 0x01f6f6f7, 0x120e0e1c, 0xa36161c2, 0x5f35356a,\
        0xf95757ae, 0xd0b9b969, 0x91868617, 0x58c1c199, 0x271d1d3a,\
        0xb99e9e27, 0x38e1e1d9, 0x13f8f8eb, 0xb398982b, 0x33111122,\
        0xbb6969d2, 0x70d9d9a9, 0x898e8e07, 0xa7949433, 0xb69b9b2d,\
        0x221e1e3c, 0x92878715, 0x20e9e9c9, 0x49cece87, 0xff5555aa,\
        0x78282850, 0x7adfdfa5, 0x8f8c8c03, 0xf8a1a159, 0x80898909,\
        0x170d0d1a, 0xdabfbf65, 0x31e6e6d7, 0xc6424284, 0xb86868d0,\
        0xc3414182, 0xb0999929, 0x772d2d5a, 0x110f0f1e, 0xcbb0b07b,\
        0xfc5454a8, 0xd6bbbb6d, 0x3a16162c)

    AES1_REVERSED = (0x50a7f451, 0x5365417e,\
    0xc3a4171a, 0x965e273a, 0xcb6bab3b, 0xf1459d1f, 0xab58faac,\
    0x9303e34b, 0x55fa3020, 0xf66d76ad, 0x9176cc88, 0x254c02f5,\
    0xfcd7e54f, 0xd7cb2ac5, 0x80443526, 0x8fa362b5, 0x495ab1de,\
    0x671bba25, 0x980eea45, 0xe1c0fe5d, 0x02752fc3, 0x12f04c81,\
    0xa397468d, 0xc6f9d36b, 0xe75f8f03, 0x959c9215, 0xeb7a6dbf,\
    0xda595295, 0x2d83bed4, 0xd3217458, 0x2969e049, 0x44c8c98e,\
    0x6a89c275, 0x78798ef4, 0x6b3e5899, 0xdd71b927, 0xb64fe1be,\
    0x17ad88f0, 0x66ac20c9, 0xb43ace7d, 0x184adf63, 0x82311ae5,\
    0x60335197, 0x457f5362, 0xe07764b1, 0x84ae6bbb, 0x1ca081fe,\
    0x942b08f9, 0x58684870, 0x19fd458f, 0x876cde94, 0xb7f87b52,\
    0x23d373ab, 0xe2024b72, 0x578f1fe3, 0x2aab5566, 0x0728ebb2,\
    0x03c2b52f, 0x9a7bc586, 0xa50837d3, 0xf2872830, 0xb2a5bf23,\
    0xba6a0302, 0x5c8216ed, 0x2b1ccf8a, 0x92b479a7, 0xf0f207f3,\
    0xa1e2694e, 0xcdf4da65, 0xd5be0506, 0x1f6234d1, 0x8afea6c4,\
    0x9d532e34, 0xa055f3a2, 0x32e18a05, 0x75ebf6a4, 0x39ec830b,\
    0xaaef6040, 0x069f715e, 0x51106ebd, 0xf98a213e, 0x3d06dd96,\
    0xae053edd, 0x46bde64d, 0xb58d5491, 0x055dc471, 0x6fd40604,\
    0xff155060, 0x24fb9819, 0x97e9bdd6, 0xcc434089, 0x779ed967,\
    0xbd42e8b0, 0x888b8907, 0x385b19e7, 0xdbeec879, 0x470a7ca1,\
    0xe90f427c, 0xc91e84f8, 0x00000000, 0x83868009, 0x48ed2b32,\
    0xac70111e, 0x4e725a6c, 0xfbff0efd, 0x5638850f, 0x1ed5ae3d,\
    0x27392d36, 0x64d90f0a, 0x21a65c68, 0xd1545b9b, 0x3a2e3624,\
    0xb1670a0c, 0x0fe75793, 0xd296eeb4, 0x9e919b1b, 0x4fc5c080,\
    0xa220dc61, 0x694b775a, 0x161a121c, 0x0aba93e2, 0xe52aa0c0,\
    0x43e0223c, 0x1d171b12, 0x0b0d090e, 0xadc78bf2, 0xb9a8b62d,\
    0xc8a91e14, 0x8519f157, 0x4c0775af, 0xbbdd99ee, 0xfd607fa3,\
    0x9f2601f7, 0xbcf5725c, 0xc53b6644, 0x347efb5b, 0x7629438b,\
    0xdcc623cb, 0x68fcedb6, 0x63f1e4b8, 0xcadc31d7, 0x10856342,\
    0x40229713, 0x2011c684, 0x7d244a85, 0xf83dbbd2, 0x1132f9ae,\
    0x6da129c7, 0x4b2f9e1d, 0xf330b2dc, 0xec52860d, 0xd0e3c177,\
    0x6c16b32b, 0x99b970a9, 0xfa489411, 0x2264e947, 0xc48cfca8,\
    0x1a3ff0a0, 0xd82c7d56, 0xef903322, 0xc74e4987, 0xc1d138d9,\
    0xfea2ca8c, 0x360bd498, 0xcf81f5a6, 0x28de7aa5, 0x268eb7da,\
    0xa4bfad3f, 0xe49d3a2c, 0x0d927850, 0x9bcc5f6a, 0x62467e54,\
    0xc2138df6, 0xe8b8d890, 0x5ef7392e, 0xf5afc382, 0xbe805d9f,\
    0x7c93d069, 0xa92dd56f, 0xb31225cf, 0x3b99acc8, 0xa77d1810,\
    0x6e639ce8, 0x7bbb3bdb, 0x097826cd, 0xf418596e, 0x01b79aec,\
    0xa89a4f83, 0x656e95e6, 0x7ee6ffaa, 0x08cfbc21, 0xe6e815ef,\
    0xd99be7ba, 0xce366f4a, 0xd4099fea, 0xd67cb029, 0xafb2a431,\
    0x31233f2a, 0x3094a5c6, 0xc066a235, 0x37bc4e74, 0xa6ca82fc,\
    0xb0d090e0, 0x15d8a733, 0x4a9804f1, 0xf7daec41, 0x0e50cd7f,\
    0x2ff69117, 0x8dd64d76, 0x4db0ef43, 0x544daacc, 0xdf0496e4,\
    0xe3b5d19e, 0x1b886a4c, 0xb81f2cc1, 0x7f516546, 0x04ea5e9d,\
    0x5d358c01, 0x737487fa, 0x2e410bfb, 0x5a1d67b3, 0x52d2db92,\
    0x335610e9, 0x1347d66d, 0x8c61d79a, 0x7a0ca137, 0x8e14f859,\
    0x893c13eb, 0xee27a9ce, 0x35c961b7, 0xede51ce1, 0x3cb1477a,\
    0x59dfd29c, 0x3f73f255, 0x79ce1418, 0xbf37c773, 0xeacdf753,\
    0x5baafd5f, 0x146f3ddf, 0x86db4478, 0x81f3afca, 0x3ec468b9,\
    0x2c342438, 0x5f40a3c2, 0x72c31d16, 0x0c25e2bc, 0x8b493c28,\
    0x41950dff, 0x7101a839, 0xdeb30c08, 0x9ce4b4d8, 0x90c15664,\
    0x6184cb7b, 0x70b632d5, 0x745c6c48, 0x4257b8d0)

    blockSize = 16

    #
    #      * Constructor.
    #      *
    #      * @param forSecurity
    #      * Used security level.
    #      * @param forEncrypt
    #      * @param blockCipherKey
    #      * @param forAad
    #      * @param iv
    #      * @param forTag
    #
    def __init__(self, forSecurity, forEncrypt, blockCipherKey, forAad, iv, forTag):
        print("__init__(forSecurity, forEncrypt, blockCipherKey")
        security = b'0x30'

        tag = forTag
        if not tag:
            #  Tag size is 12 bytes.
            tag = bytearray(12)
        elif len(tag) != 12:
            raise ValueError("Invalid tag.")
        self.encrypt = True
        self.workingKey = self.generateKey(self.encrypt, b'bbbbbbbbbbbbbbbb')
        print(self.workingKey )
        if self.encrypt:
            bufLength = GXDLMSChipperingStream.BLOCK_SIZE
        else:
            bufLength = GXDLMSChipperingStream.BLOCK_SIZE + GXDLMSChipperingStream.TAG_SIZE
        self.bufBlock = bytearray(bufLength)
        self.aad = forAad
        self.h = bytearray(GXDLMSChipperingStream.BLOCK_SIZE)
        print(self.h)
        iv = iv
        if iv:
            self.processBlock(self.h, 0, self.h, 0)
            self.mArray = [[None] * 32] * 32
            self.init(self.h)
            self.j0 = bytearray(16)
            self.j0[0:len(iv)] = iv[0:]
            self.j0[15] = 0x01
        if self.aad:
            self.s = self.getGHash(aad)
        if iv:
            self.counter = self.clone(self.j0)
        self.bytesRemaining = 0
        self.totalLength = 0
        self.output = GXByteBuffer()
        print(self.output)

        self.c0 = self.c1 = self.c2 = self.c3 = 0
        self.blockSize = 16
        
    @classmethod
    def clone(cls, value):
        """
        Clone byte array.
        """
        tmp = value[0:]
        return tmp

    #
    #      * Convert byte array to Little Endian.
    #      *
    #      * @param data
    #      * @param offset
    #      * @return
    #
    @classmethod
    def toUInt32(cls, value, offset):
        tmp = value[offset] & 0xFF
        tmp |= (value[offset + 1] << 8) & 0xFF00
        tmp |= (value[offset + 2] << 16) & 0xFF0000
        tmp |= (value[offset + 3] << 24) & 0xFF000000
        return tmp

    @classmethod
    def subWord(cls, value):
        tmp = cls.S_BOX[value & 0xFF] & 0xFF
        tmp |= (((cls.S_BOX[(value >> 8) & 0xFF]) & 0xFF) << 8) & 0xFF00
        tmp |= (((cls.S_BOX[(value >> 16) & 0xFF]) & 0xFF) << 16) & 0xFF0000
        tmp |= (((cls.S_BOX[(value >> 24) & 0xFF]) & 0xFF) << 24) & 0xFF000000
        return tmp

    @classmethod
    def shift(cls, value, shift):
        """
        Shift value.
        """
        return (value >> shift) | (value << (32 - shift)) & 0xFFFFFFFF

    #
    #      * Initialise the key schedule from the user supplied key.
    #      *
    #      * @return
    #
    @classmethod
    def starX(cls, value):
        m1 = 0x80808080
        m2 = 0x7f7f7f7f
        m3 = 0x0000001b
        return ((value & m2) << 1) ^ (((value & m1) >> 7) * m3)

    def imixCol(self, x):
        f2 = self.starX(x)
        f4 = self.starX(f2)
        f8 = self.starX(f4)
        f9 = x ^ f8
        return f2 ^ f4 ^ f8 ^ self.shift(f2 ^ f9, 8) ^ self.shift(f4 ^ f9, 16) ^ self.shift(f9, 24)

    #
    #      * Get bytes from UIn32.
    #      *
    #      * @param value
    #      * @param data
    #      * @param offset
    #
    @classmethod
    def getUInt32(cls, value, data, offset):
        data[offset] = value & 0xFF
        data[offset + 1] = (value >> 8) & 0xFF
        data[offset + 2] = (value >> 16) & 0xFF
        data[offset + 3] = (value >> 24) & 0xFF

    def unPackBlock(self, bytes_, offset):
        self.c0 = self.toUInt32(bytes_, offset)
        self.c1 = self.toUInt32(bytes_, offset + 4)
        self.c2 = self.toUInt32(bytes_, offset + 8)
        self.c3 = self.toUInt32(bytes_, offset + 12)

    def packBlock(self, bytes_, offset):
        self.getUInt32(self.c0, bytes_, offset)
        self.getUInt32(self.c1, bytes_, offset + 4)
        self.getUInt32(self.c2, bytes_, offset + 8)
        self.getUInt32(self.c3, bytes_, offset + 12)

    #
    #      * Encrypt data block.
    #      *
    #      * @param key
    #
    def encryptBlock(self, key):
        r = 1
        self.c0 ^= key[0][0]
        self.c1 ^= key[0][1]
        self.c2 ^= key[0][2]
        self.c3 ^= key[0][3]
        while r < self.rounds - 1:
            r0 = self.AES[self.c0 & 0xFF] & 0xFFFFFFFF
            r0 ^= self.shift(self.AES[(self.c1 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            r0 ^= self.shift(self.AES[(self.c2 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            r0 ^= self.shift(self.AES[(self.c3 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            r0 ^= key[r][0] & 0xFFFFFFFF
            r1 = self.AES[self.c1 & 0xFF] & 0xFFFFFFFF
            r1 ^= self.shift(self.AES[(self.c2 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            r1 ^= self.shift(self.AES[(self.c3 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            r1 ^= self.shift(self.AES[(self.c0 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            r1 ^= key[r][1] & 0xFFFFFFFF
            r2 = self.AES[self.c2 & 0xFF] & 0xFFFFFFFF
            r2 ^= self.shift(self.AES[(self.c3 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            r2 ^= self.shift(self.AES[(self.c0 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            r2 ^= self.shift(self.AES[(self.c1 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            r2 ^= key[r][2] & 0xFFFFFFFF
            r3 = self.AES[self.c3 & 0xFF] & 0xFFFFFFFF
            r3 ^= self.shift(self.AES[(self.c0 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            r3 ^= self.shift(self.AES[(self.c1 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            r3 ^= self.shift(self.AES[(self.c2 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            r3 ^= key[r][3] & 0xFFFFFFFF
            r = r + 1
            self.c0 = self.AES[r0 & 0xFF] & 0xFFFFFFFF
            self.c0 ^= self.shift(self.AES[(r1 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            self.c0 ^= self.shift(self.AES[(r2 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            self.c0 ^= self.shift(self.AES[(r3 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            self.c0 ^= key[r][0] & 0xFFFFFFFF
            self.c1 = self.AES[r1 & 0xFF] & 0xFFFFFFFF
            self.c1 ^= self.shift(self.AES[(r2 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            self.c1 ^= self.shift(self.AES[(r3 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            self.c1 ^= self.shift(self.AES[(r0 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            self.c1 ^= key[r][1] & 0xFFFFFFFF
            self.c2 = self.AES[r2 & 0xFF] & 0xFFFFFFFF
            self.c2 ^= self.shift(self.AES[(r3 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            self.c2 ^= self.shift(self.AES[(r0 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            self.c2 ^= self.shift(self.AES[(r1 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            self.c2 ^= key[r][2] & 0xFFFFFFFF
            self.c3 = self.AES[r3 & 0xFF] & 0xFFFFFFFF
            self.c3 ^= self.shift(self.AES[(r0 >> 8) & 0xFF], 24) & 0xFFFFFFFF
            self.c3 ^= self.shift(self.AES[(r1 >> 16) & 0xFF], 16) & 0xFFFFFFFF
            self.c3 ^= self.shift(self.AES[(r2 >> 24) & 0xFF], 8) & 0xFFFFFFFF
            self.c3 ^= key[r][3] & 0xFFFFFFFF
            r = r + 1

        r0 = self.AES[self.c0 & 0xFF] & 0xFFFFFFFF
        r0 ^= self.shift(self.AES[(self.c1 >> 8) & 0xFF], 24) & 0xFFFFFFFF
        r0 ^= self.shift(self.AES[(self.c2 >> 16) & 0xFF], 16) & 0xFFFFFFFF
        r0 ^= self.shift(self.AES[self.c3 >> 24], 8) & 0xFFFFFFFF
        r0 ^= key[r][0] & 0xFFFFFFFF
        r1 = self.AES[self.c1 & 0xFF] & 0xFFFFFFFF
        r1 ^= self.shift(self.AES[(self.c2 >> 8) & 0xFF], 24) & 0xFFFFFFFF
        r1 ^= self.shift(self.AES[(self.c3 >> 16) & 0xFF], 16) & 0xFFFFFFFF
        r1 ^= self.shift(self.AES[self.c0 >> 24], 8) & 0xFFFFFFFF
        r1 ^= key[r][1] & 0xFFFFFFFF
        r2 = self.AES[self.c2 & 0xFF] & 0xFFFFFFFF
        r2 ^= self.shift(self.AES[(self.c3 >> 8) & 0xFF], 24) & 0xFFFFFFFF
        r2 ^= self.shift(self.AES[(self.c0 >> 16) & 0xFF], 16) & 0xFFFFFFFF
        r2 ^= self.shift(self.AES[self.c1 >> 24], 8) & 0xFFFFFFFF
        r2 ^= key[r][2] & 0xFFFFFFFF
        r3 = self.AES[self.c3 & 0xFF] & 0xFFFFFFFF
        r3 ^= self.shift(self.AES[(self.c0 >> 8) & 0xFF], 24) & 0xFFFFFFFF
        r3 ^= self.shift(self.AES[(self.c1 >> 16) & 0xFF], 16) & 0xFFFFFFFF
        r3 ^= self.shift(self.AES[self.c2 >> 24], 8) & 0xFFFFFFFF
        r3 ^= key[r][3] & 0xFFFFFFFF
        r += 1
        self.c0 = (self.S_BOX[r0 & 0xFF] & 0xFF) & 0xFFFFFFFF
        self.c0 ^= ((self.S_BOX[(r1 >> 8) & 0xFF] & 0xFF) << 8) & 0xFFFFFFFF
        self.c0 ^= ((self.S_BOX[(r2 >> 16) & 0xFF] & 0xFF) << 16) & 0xFFFFFFFF
        self.c0 ^= ((self.S_BOX[r3 >> 24] & 0xFF) << 24) & 0xFFFFFFFF
        self.c0 ^= key[r][0] & 0xFFFFFFFF
        self.c1 = (self.S_BOX[r1 & 0xFF] & 0xFF) & 0xFFFFFFFF
        self.c1 ^= ((self.S_BOX[(r2 >> 8) & 0xFF] & 0xFF) << 8) & 0xFFFFFFFF
        self.c1 ^= ((self.S_BOX[(r3 >> 16) & 0xFF] & 0xFF) << 16) & 0xFFFFFFFF
        self.c1 ^= ((self.S_BOX[r0 >> 24] & 0xFF) << 24) & 0xFFFFFFFF
        self.c1 ^= key[r][1] & 0xFFFFFFFF
        self.c2 = (self.S_BOX[r2 & 0xFF] & 0xFF) & 0xFFFFFFFF
        self.c2 ^= ((self.S_BOX[(r3 >> 8) & 0xFF] & 0xFF) << 8) & 0xFFFFFFFF
        self.c2 ^= ((self.S_BOX[(r0 >> 16) & 0xFF] & 0xFF) << 16) & 0xFFFFFFFF
        self.c2 ^= ((self.S_BOX[r1 >> 24] & 0xFF) << 24) & 0xFFFFFFFF
        self.c2 ^= key[r][2] & 0xFFFFFFFF
        self.c3 = (self.S_BOX[r3 & 0xFF] & 0xFF) & 0xFFFFFFFF
        self.c3 ^= ((self.S_BOX[(r0 >> 8) & 0xFF] & 0xFF) << 8) & 0xFFFFFFFF
        self.c3 ^= ((self.S_BOX[(r1 >> 16) & 0xFF] & 0xFF) << 16) & 0xFFFFFFFF
        self.c3 ^= ((self.S_BOX[r2 >> 24] & 0xFF) << 24) & 0xFFFFFFFF
        self.c3 ^= key[r][3] & 0xFFFFFFFF
        print(self.c3)

    def decryptBlock(self, key):
        t0 = self.c0 ^ key[self.rounds][0]
        t1 = self.c1 ^ key[self.rounds][1]
        t2 = self.c2 ^ key[self.rounds][2]
        r0 = r1 = r2 = 0
        r3 = self.c3 ^ key[self.rounds][3]
        r = self.rounds - 1
        while r > 1:
            r0 = (self.AES1_REVERSED[t0 & 255] & 0xFFFFFFFF) ^ self.shift(self.AES1_REVERSED[(r3 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t2 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t1 >> 24) & 255], 8) ^ key[r][0]
            r1 = self.AES1_REVERSED[t1 & 255] ^ self.shift(self.AES1_REVERSED[(t0 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r3 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t2 >> 24) & 255], 8) ^ key[r][1]
            r2 = self.AES1_REVERSED[t2 & 255] ^ self.shift(self.AES1_REVERSED[(t1 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t0 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r3 >> 24) & 255], 8) ^ key[r][2]
            r3 = self.AES1_REVERSED[r3 & 255] ^ self.shift(self.AES1_REVERSED[(t2 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t1 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t0 >> 24) & 255], 8) ^ key[r][3]
            r -= 1
            t0 = self.AES1_REVERSED[r0 & 255] ^ self.shift(self.AES1_REVERSED[(r3 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r2 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r1 >> 24) & 255], 8) ^ key[r][0]
            t1 = self.AES1_REVERSED[r1 & 255] ^ self.shift(self.AES1_REVERSED[(r0 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r3 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r2 >> 24) & 255], 8) ^ key[r][1]
            t2 = self.AES1_REVERSED[r2 & 255] ^ self.shift(self.AES1_REVERSED[(r1 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r0 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r3 >> 24) & 255], 8) ^ key[r][2]
            r3 = self.AES1_REVERSED[r3 & 255] ^ self.shift(self.AES1_REVERSED[(r2 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r1 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r0 >> 24) & 255], 8) ^ key[r][3]
            r -= 1
        r = 1
        r0 = self.AES1_REVERSED[t0 & 255] ^ self.shift(self.AES1_REVERSED[(r3 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t2 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t1 >> 24) & 255], 8) ^ key[r][0]
        r1 = self.AES1_REVERSED[t1 & 255] ^ self.shift(self.AES1_REVERSED[(t0 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(r3 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t2 >> 24) & 255], 8) ^ key[r][1]
        r2 = self.AES1_REVERSED[t2 & 255] ^ self.shift(self.AES1_REVERSED[(t1 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t0 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(r3 >> 24) & 255], 8) ^ key[r][2]
        r3 = self.AES1_REVERSED[r3 & 255] ^ self.shift(self.AES1_REVERSED[(t2 >> 8) & 255], 24) ^ self.shift(self.AES1_REVERSED[(t1 >> 16) & 255], 16) ^ self.shift(self.AES1_REVERSED[(t0 >> 24) & 255], 8) ^ key[r][3]
        r = 0
        self.c0 = (self.S_BOX_REVERSED[r0 & 255] & 0xFF) ^ ((((self.S_BOX_REVERSED[(r3 >> 8) & 255]) & 0xFF) << 8)) ^ ((((self.S_BOX_REVERSED[(r2 >> 16) & 255]) & 0xFF) << 16)) ^ ((((self.S_BOX_REVERSED[(r1 >> 24) & 255]) & 0xFF) << 24)) ^ key[r][0]
        self.c1 = (self.S_BOX_REVERSED[r1 & 255] & 0xFF) ^ (((self.S_BOX_REVERSED[(r0 >> 8) & 255]) & 0xFF) << 8) ^ (((self.S_BOX_REVERSED[(r3 >> 16) & 255]) & 0xFF) << 16) ^ (((self.S_BOX_REVERSED[(r2 >> 24) & 255]) & 0xFF) << 24) ^ key[r][1]
        self.c2 = (self.S_BOX_REVERSED[r2 & 255] & 0xFF) ^ (((self.S_BOX_REVERSED[(r1 >> 8) & 255]) & 0xFF) << 8) ^ (((self.S_BOX_REVERSED[(r0 >> 16) & 255]) & 0xFF) << 16) ^ (((self.S_BOX_REVERSED[(r3 >> 24) & 255]) & 0xFF) << 24) ^ key[r][2]
        self.c3 = (self.S_BOX_REVERSED[r3 & 255] & 0xFF) ^ (((self.S_BOX_REVERSED[(r2 >> 8) & 255]) & 0xFF) << 8) ^ (((self.S_BOX_REVERSED[(r1 >> 16) & 255]) & 0xFF) << 16) ^ (((self.S_BOX_REVERSED[(r0 >> 24) & 255]) & 0xFF) << 24) ^ key[r][3]

    def processBlock(self, input_, inOffset, forOutput, outOffset):
        if inOffset + (32 / 2) > len(input_):
            raise ValueError("input buffer too short")
        if outOffset + (32 / 2) > len(forOutput):
            raise ValueError("output buffer too short")
        self.unPackBlock(input_, inOffset)
        if self.encrypt:
            self.encryptBlock(self.workingKey)
        else:
            self.decryptBlock(self.workingKey)
        self.packBlock(forOutput, outOffset)
        return self.BLOCK_SIZE

    @classmethod
    def bEToUInt32(cls, buff, offset):
        value = (buff[offset] << 24)
        value |= (buff[offset + 1] << 16) & 0xFF0000
        value |= (buff[offset + 2] << 8) & 0xFF00
        value |= buff[offset + 3] & 0xFF
        return value

    @classmethod
    def shiftRight(cls, block, count):
        bit = 0
        i = 0
        while i < 4:
            b = block[i]
            block[i] = (b >> count) | bit
            bit = (b << (32 - count)) & 0xFFFFFFFF
            i += 1

    @classmethod
    def multiplyP(cls, x):
        lsb = (x[3] & 1) != 0
        cls.shiftRight(x, 1)
        if lsb:
            x[0] ^= 0xe1000000

    @classmethod
    def getUint128(cls, buff):
        us = [None] * 4
        us[0] = cls.bEToUInt32(buff, 0)
        us[1] = cls.bEToUInt32(buff, 4)
        us[2] = cls.bEToUInt32(buff, 8)
        us[3] = cls.bEToUInt32(buff, 12)
        return us

    @classmethod
    def xor(cls, block, value):
        pos = 0
        while pos != 16:
            block[pos] ^= value[pos]
            pos += 1

    @classmethod
    def xor128(cls, block, value):
        pos = 0
        while pos != 4:
            block[pos] ^= value[pos]
            pos += 1

    @classmethod
    def multiplyP8(cls, x):
        lsw = x[3]
        cls.shiftRight(x, 8)
        pos = 0
        while pos != 8:
            if (lsw & (1 << pos)) != 0:
                x[0] ^= ((0xe1000000 >> (7 - pos)) & 0xFFFFFFFF)
            pos += 1

    def getGHash(self, b):
        y = bytearray(16)
        pos = 0
        while pos < len(b):
            x = bytearray(16)
            cnt = min(len(b) - pos, 16)
            x[0:cnt] = b[pos:pos + cnt]
            self.xor(y, x)
            self.multiplyH(y)
            pos += 16
        return y

    @classmethod
    def uInt32ToBE(cls, value, buff, offset):
        buff[offset] = (value >> 24) & 0xFF
        buff[offset + 1] = (value >> 16) & 0xFF
        buff[offset + 2] = (value >> 8) & 0xFF
        buff[offset + 3] = value & 0xFF

    def multiplyH(self, value):
        tmp = [0] * 4
        pos = 0
        while pos != 16:
            m = self.mArray[pos + pos][value[pos] & 0x0f]
            tmp[0] ^= m[0]
            tmp[1] ^= m[1]
            tmp[2] ^= m[2]
            tmp[3] ^= m[3]
            m = self.mArray[pos + pos + 1][(value[pos] & 0xf0) >> 4]
            tmp[0] ^= m[0]
            tmp[1] ^= m[1]
            tmp[2] ^= m[2]
            tmp[3] ^= m[3]
            pos += 1
        self.uInt32ToBE(tmp[0], value, 0)
        self.uInt32ToBE(tmp[1], value, 4)
        self.uInt32ToBE(tmp[2], value, 8)
        self.uInt32ToBE(tmp[3], value, 12)

    def init(self, value):
        self.mArray[0] = [0] * 16
        self.mArray[1] = [0] * 16
        self.mArray[0][0] = [0] * 4
        self.mArray[1][0] = [0] * 4
        self.mArray[1][8] = self.getUint128(value)
        tmp = []
        pos = 4
        while pos >= 1:
            tmp = self.clone(self.mArray[1][pos + pos])
            self.multiplyP(tmp)
            self.mArray[1][pos] = tmp
            pos >>= 1
        tmp = self.clone(self.mArray[1][1])
        self.multiplyP(tmp)
        self.mArray[0][8] = tmp
        pos = 4
        while pos >= 1:
            tmp = self.clone(self.mArray[0][pos + pos])
            self.multiplyP(tmp)
            self.mArray[0][pos] = tmp
            pos >>= 1
        pos1 = 0
        while True:
            pos2 = 2
            while pos2 < 16:
                k = 1
                while k < pos2:
                    tmp = self.clone(self.mArray[pos1][pos2])
                    self.xor128(tmp, self.mArray[pos1][k])
                    self.mArray[pos1][pos2 + k] = tmp
                    k += 1
                pos2 += pos2
            pos1 += 1
            if pos1 == 32:
                return
            if pos1 > 1:
                self.mArray[pos1] = [0] * 16
                self.mArray[pos1][0] = [0] * 4
                pos = 8
                while pos > 0:
                    tmp = self.clone(self.mArray[pos1 - 2][pos])
                    self.multiplyP8(tmp)
                    self.mArray[pos1][pos] = tmp
                    pos >>= 1


    def gCTRBlock(self, buf, bufCount):
        i = 15
        while i >= 12:
            self.counter[i] += 1
            if self.counter[i] != 0:
                break
            i -= 1
        tmp = bytearray(self.BLOCK_SIZE)
        self.processBlock(self.counter, 0, tmp, 0)
        print("tmp: ", tmp)
        if self.encrypt:
            zeroes = bytearray(self.BLOCK_SIZE)
            tmp[bufCount:self.BLOCK_SIZE] = zeroes[bufCount:self.BLOCK_SIZE]
            hashBytes = tmp
        else:
            hashBytes = buf
        pos = 0
        while pos != bufCount:
            tmp[pos] ^= buf[pos]
            self.output.setUInt8(tmp[pos])
            pos += 1
        self.xor(self.s, hashBytes)
        self.multiplyH(self.s)
        self.totalLength += bufCount
        print(self.s)
    @classmethod
    def setPackLength(cls, length, buff, offset):
        cls.uInt32ToBE(int((length >> 32)), buff, offset)
        cls.uInt32ToBE(int(length), buff, offset + 4)

    def reset(self):
        self.s = self.getGHash(self.aad)
        self.counter = self.clone(self.j0)
        self.bytesRemaining = 0
        self.totalLength = 0

    @classmethod
    def tagsEquals(cls, tag1, tag2):
        pos = 0
        while pos != 12:
            if tag1[pos] != tag2[pos]:
                return False
            pos += 1
        return True

    def write(self, input_):
        print("ch")
        for it in input_:
            self.bufBlock[self.bytesRemaining] = it
            self.bytesRemaining += 1
            if self.bytesRemaining == self.BLOCK_SIZE:
                self.gCTRBlock(self.bufBlock, self.BLOCK_SIZE)
                if not self.encrypt:
                    #System.arraycopy(self.bufBlock, self.BLOCK_SIZE,
                    #self.bufBlock, 0,)
                    self.bufBlock[0:len(self.tag)] = self.bufBlock[self.blockSize:self.blockSize + len(self.tag)]
                self.bytesRemaining = 0
        print(self.BLOCK_SIZE)

    def flushFinalBlock(self):
        if self.bytesRemaining > 0:
            tmp = self.bufBlock[0:self.bytesRemaining]
            self.gCTRBlock(tmp, self.bytesRemaining)
        # if self.security == Security.ENCRYPTION:
        #     self.reset()
        #     return self.output.array()
        x = bytearray(16)
        self.setPackLength(8 * len(self.aad), x, 0)
        self.setPackLength(self.totalLength * 8, x, 8)
        self.xor(self.s, x)
        self.multiplyH(self.s)
        generatedTag = bytearray(self.BLOCK_SIZE)
        self.processBlock(self.j0, 0, generatedTag, 0)
        print(generatedTag)
        self.xor(generatedTag, self.s)
        if not self.encrypt:
            if not self.tagsEquals(self.tag, generatedTag):
                print(GXByteBuffer.hex(self.tag, False) + "-" + GXByteBuffer.hex(generatedTag, False))
                raise ValueError("Decrypt failed. Invalid tag.")
        else:
            #Tag size is 12 bytes.
            self.tag = generatedTag[0:12]
        self.reset()
        print(self.tag.hex())
        return self.tag.hex()

    def generateKey(self, isEncrypt, key):
        #Key length in words.
        keyLen = int(len(key) / 4)
        self.rounds = keyLen + 6
        w = [[0 for x in range(4)] for y in range(self.rounds + 1)]
        t = 0
        i = 0
        while i < len(key):
            w[t >> 2][t & 3] = self.toUInt32(key, i)
            i += 4
            t += 1
        k = (self.rounds + 1) << 2
        i = keyLen
        while i < k:
            temp = w[(i - 1) >> 2][(i - 1) & 3]
            if (i % keyLen) == 0:
                temp = self.subWord(self.shift(temp, 8)) ^ (self.R_CON[int(i / keyLen) - 1] & 0xFF)
            elif (keyLen > 6) and ((i % keyLen) == 4):
                temp = self.subWord(temp)
            w[i >> 2][i & 3] = w[(i - keyLen) >> 2][(i - keyLen) & 3] ^ temp
            i += 1
        if not isEncrypt:
            j = 1
            while j < self.rounds:
                i = 0
                while i < 4:
                    w[j][i] = self.imixCol(w[j][i])
                    i += 1
                j += 1
        print(w)        
        return w

    @classmethod
    def galoisMultiply(cls, value):
        if value >> 7 != 0:
            value = value << 1
            return (value ^ 0x1b) & 0xFF

        return (value << 1) & 0xFF
#        temp = (value >> 7) & 0xFF
#        temp = temp & 0x1b
#        return ((value << 1) ^ temp) & 0xFF

    @classmethod
    def aes1Encrypt(cls, data, offset, secret):
        round_ = 0
        i = 0
        key = secret[0:]
        while round_ < 10:
            i = 0
            while i < 16:
                data[i + offset] = cls.S_BOX[(data[i + offset] ^ key[i]) & 0xFF]
                i += 1
            buf1 = data[1 + offset]
            data[1 + offset] = data[5 + offset]
            data[5 + offset] = data[9 + offset]
            data[9 + offset] = data[13 + offset]
            data[13 + offset] = buf1
            buf1 = data[2 + offset]
            buf2 = data[6 + offset]
            data[2 + offset] = data[10 + offset]
            data[6 + offset] = data[14 + offset]
            data[10 + offset] = buf1
            data[14 + offset] = buf2
            buf1 = data[15 + offset]
            data[15 + offset] = data[11 + offset]
            data[11 + offset] = data[7 + offset]
            data[7 + offset] = data[3 + offset]
            data[3 + offset] = buf1
            if round_ < 9:
                i = 0
                while i < 4:
                    buf4 = (i << 2) & 0xFF
                    buf1 = (data[buf4 + offset] ^ data[buf4 + 1 + offset] ^ data[buf4 + 2 + offset] ^ data[buf4 + 3 + offset]) & 0xFF
                    buf2 = data[buf4 + offset] & 0xFF
                    buf3 = (data[buf4 + offset] ^ data[buf4 + 1 + offset]) & 0xFF
                    buf3 = cls.galoisMultiply(buf3) & 0xFF
                    data[buf4 + offset] = (data[buf4 + offset] ^ buf3 ^ buf1) & 0xFF
                    buf3 = (data[buf4 + 1 + offset] ^ data[buf4 + 2 + offset]) & 0xFF
                    buf3 = cls.galoisMultiply(buf3) & 0xFF
                    data[buf4 + 1 + offset] = (data[buf4 + 1 + offset] ^ buf3 ^ buf1) & 0xFF
                    buf3 = (data[buf4 + 2 + offset] ^ data[buf4 + 3 + offset]) & 0xFF
                    buf3 = cls.galoisMultiply(buf3) & 0xFF
                    data[buf4 + 2 + offset] = (data[buf4 + 2 + offset] ^ buf3 ^ buf1) & 0xFF
                    buf3 = (data[buf4 + 3 + offset] ^ buf2) & 0xFF
                    buf3 = cls.galoisMultiply(buf3) & 0xFF
                    data[buf4 + 3 + offset] = (data[buf4 + 3 + offset] ^ buf3 ^ buf1) & 0xFF
                    i += 1
            key[0] = (cls.S_BOX[key[13] & 0xFF] ^ key[0] ^ cls.R_CON[round_]) & 0xFF
            key[1] = (cls.S_BOX[key[14] & 0xFF] ^ key[1]) & 0xFF
            key[2] = (cls.S_BOX[key[15] & 0xFF] ^ key[2]) & 0xFF
            key[3] = (cls.S_BOX[key[12] & 0xFF] ^ key[3]) & 0xFF
            i = 4
            while i < 16:
                key[i] = (key[i] ^ key[i - 4]) & 0xFF
                i += 1
            round_ += 1
        i = 0
        while i < 16:
            data[i + offset] = (data[i + offset] ^ key[i])
            i += 1

    def encryptAes(self, data):
        n = len(data) / 8
        if (n * 8) != len(data):
            raise ValueError("Invalid data.")
        iv = bytearray([0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6])
        block = bytearray(len(data) + len(iv))
        buf = bytearray(8 + len(iv))
        block[0:len(self.IV)] = self.IV[0:len(self.IV)]
        block[len(self.IV):len(self.IV) + len(data)] = data[0:len(data)]
        j = 0
        while j != 6:
            i = 1
            while i <= n:
                buf[0:len(self.IV)] = block[0: len(self.IV)]
                buf[len(self.IV):8 + len(self.IV)] = block[8 * i:8 * i + 8]
                self.processBlock(buf, 0, buf, 0)
                t = int(n * j + i)
                k = 1
                while t != 0:
                    v = int(t)
                    buf[len(self.IV) - k] ^= v
                    t = int(t >> 8)
                    k += 1
                block[0:8] = buf[0:8]
                block[8 * i:8 * i + 8] = buf[8:16]
                i += 1
            j += 1
        return block

    def decryptAes(self, input_):
        n = len(input_) / 8
        if (n * 8) != len(input_):
            raise ValueError("Invalid data.")
        iv = bytearray([0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6])
        if len(input_) > len(iv):
            block = bytearray(len(input_) - len(iv))
        else:
            block = bytearray(len(iv))
        a = bytearray(len(iv))
        buf = bytearray(8 + len(iv))
        a[0:] = input_[0:len(iv)]
        block[0:] = input_[len(iv):len(input_)]
        n = n - 1
        if n == 0:
            n = 1
        j = 5
        while j >= 0:
            i = n
            while i >= 1:
                buf[0:len(iv)] = a[0:len(iv)]
                buf[len(iv):8 + len(iv)] = block[8 * int(i - 1):8 * int(i)]
                t = n * j + i
                k = 1
                while t != 0:
                    v = int(t)
                    buf[len(self.IV)] ^= v
                    t = int((int(t) >> 8))
                    k += 1
                self.processBlock(buf, 0, buf, 0)
                a[0:] = buf[0:8]
                block[8:16] = buf[8 * (i - 1):8*i]
                i -= 1
            j -= 1
        if a != self.IV:
            raise ValueError("Invalid data")
        return block

    @classmethod
    def aes1Decrypt(cls, data, secret):
        buf1 = 0
        buf2 = 0
        buf3 = 0
        round_ = 0
        i = 0
        buf4 = 0
        key = secret[0:]
        while round_ < 10:
            key[0] = int((cls.S_BOX[key[13] & 0xFF] ^ key[0] ^ cls.R_CON[round_]))
            key[1] = int((cls.S_BOX[key[14] & 0xFF] ^ key[1]))
            key[2] = int((cls.S_BOX[key[15] & 0xFF] ^ key[2]))
            key[3] = int((cls.S_BOX[key[12] & 0xFF] ^ key[3]))
            while i < 16:
                key[i] = int((key[i] ^ key[i - 4]))
                i += 1
            round_ += 1
        while i < 16:
            data[i] = int((data[i] ^ key[i]))
            i += 1
        while round_ < 10:
            while i > 3:
                key[i] = int((key[i] ^ key[i - 4]))
                i -= 1
            key[0] = int((cls.S_BOX[key[13] & 0xFF] ^ key[0] ^ cls.R_CON[9 - round_]))
            key[1] = int((cls.S_BOX[key[14] & 0xFF] ^ key[1]))
            key[2] = int((cls.S_BOX[key[15] & 0xFF] ^ key[2]))
            key[3] = int((cls.S_BOX[key[12] & 0xFF] ^ key[3]))
            if round_ > 0:
                while i < 4:
                    buf4 = (i << 2) & 0xFF
                    buf1 = cls.galoisMultiply(cls.galoisMultiply(data[buf4] ^ data[buf4 + 2]))
                    buf2 = cls.galoisMultiply(cls.galoisMultiply(data[buf4 + 1] ^ data[buf4 + 3]))
                    data[buf4] ^= buf1
                    data[buf4 + 1] ^= buf2
                    data[buf4 + 2] ^= buf1
                    data[buf4 + 3] ^= buf2
                    buf1 = int((data[buf4] ^ data[buf4 + 1] ^ data[buf4 + 2] ^ data[buf4 + 3]))
                    buf2 = data[buf4]
                    buf3 = int((data[buf4] ^ data[buf4 + 1]))
                    buf3 = cls.galoisMultiply(buf3)
                    data[buf4] = int((data[buf4] ^ buf3 ^ buf1))
                    buf3 = int((data[buf4 + 1] ^ data[buf4 + 2]))
                    buf3 = cls.galoisMultiply(buf3)
                    data[buf4 + 1] = int((data[buf4 + 1] ^ buf3 ^ buf1))
                    buf3 = int((data[buf4 + 2] ^ data[buf4 + 3]))
                    buf3 = cls.galoisMultiply(buf3)
                    data[buf4 + 2] = int((data[buf4 + 2] ^ buf3 ^ buf1))
                    buf3 = int((data[buf4 + 3] ^ buf2))
                    buf3 = cls.galoisMultiply(buf3)
                    data[buf4 + 3] = int((data[buf4 + 3] ^ buf3 ^ buf1))
                    i += 1
            buf1 = data[13]
            data[13] = data[9]
            data[9] = data[5]
            data[5] = data[1]
            data[1] = buf1
            buf1 = data[10]
            buf2 = data[14]
            data[10] = data[2]
            data[14] = data[6]
            data[2] = buf1
            data[6] = buf2
            buf1 = data[3]
            data[3] = data[7]
            data[7] = data[11]
            data[11] = data[15]
            data[15] = buf1
            while i < 16:
                data[i] = int((cls.S_BOX_REVERSED[data[i] & 0xFF] ^ key[i]))
                i += 1
            round_ += 1
# /////////////////////////////////////////////////////////////////////////////
#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#pylint: disable=broad-except
try:
    from enum import IntEnum
    class GXIntEnum(IntEnum):
        """Enum class."""
except Exception:
    class GXIntEnum(int):
        """Enum class."""

class CountType(GXIntEnum):
    """
    Enumerate values that are add to counted GMAC.
    """

    # Total packet is created.
    PACKET = -1

    # Counted Tag is added.
    TAG = 0x1

    # Data is added.
    DATA = 0x2

#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#pylint: disable=broad-except
try:
    from enum import IntEnum
    class GXIntEnum(IntEnum):
        """Enum class."""
except Exception:
    class GXIntEnum(int):
        """Enum class."""

class SecuritySuite(GXIntEnum):
    """
    Security suite Specifies authentication, encryption and key wrapping algorithm.
    """
    #pylint: disable=too-few-public-methods

    #
    # AES-GCM-128 for authenticated encryption and AES-128 for key wrapping.
    #
    # A.K.A Security Suite 0.
    #
    AES_GCM_128 = 0

    #
    # ECDH-ECDSAAES-GCM-128SHA-256.
    # A.K.A Security Suite 1.
    #
    ECDH_ECDSA_AES_GCM_128_SHA_256 = 1

    #
    # ECDH-ECDSAAES-GCM-256SHA-384.
    # A.K.A Security Suite 2.
    #
    ECDHE_CDSA_AES_GCM_256_SHA_384 = 2

#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#pylint: disable=broad-except,no-name-in-module
from datetime import datetime
# from ..GXTimeZone import GXTimeZone
# from ._GXDataInfo import _GXDataInfo
# from ..GXByteBuffer import GXByteBuffer
# from ..GXBitString import GXBitString
# from ..enums import DataType
# from ..enums import DateTimeSkips, DateTimeExtraInfo, ClockStatus
# from ..TranslatorTags import TranslatorTags
# from ..TranslatorOutputType import TranslatorOutputType
# from ..GXArray import GXArray
# from ..GXStructure import GXStructure
# from ..enums.Standard import Standard
# from ..GXEnum import GXEnum
# from ..GXInt8 import GXInt8
# from ..GXInt16 import GXInt16
# from ..GXInt32 import GXInt32
# from ..GXInt64 import GXInt64
# from ..GXUInt8 import GXUInt8
# from ..GXUInt16 import GXUInt16
# from ..GXUInt32 import GXUInt32
# from ..GXUInt64 import GXUInt64
# from ..GXDateTime import GXDateTime
# from ..GXDate import GXDate
# from ..GXTime import GXTime
# from ..GXFloat32 import GXFloat32
# from ..GXFloat64 import GXFloat64

# pylint: disable=too-many-public-methods
class _GXCommon:
    """This class is for internal use only and is subject to changes or removal
    in future versions of the API.  Don't use it."""

    #      HDLC frame start and end character.
    HDLC_FRAME_START_END = 0x7E
    LLC_SEND_BYTES = bytearray([0xE6, 0xE6, 0x00])
    LLC_REPLY_BYTES = bytearray([0xE6, 0xE7, 0x00])
    DATA_TYPE_OFFSET = 0xFF0000
    zeroes = "00000000000000000000000000000000"


    @classmethod
    def getBytes(cls, value):
        """
        Convert string to byte array.
        value: String value.
        returns String as bytes.
        """
        if not value:
            return None
        return value.encode()

    #
    # Is string hex string.
    #
    # value: String value.
    # Return true, if string is hex string.
    #
    @classmethod
    def isHexString(cls, value):
        # pylint: disable=chained-comparison
        if not value:
            return False
        ch = str()
        pos = 0
        while pos != len(value):
            ch = value.charAt(pos)
            if ch != ' ':
                if not ((ch > 0x40 and ch < 'G') or (ch > 0x60 and ch < 'g') or (ch > '/' and ch < ':')):
                    return False
            pos += 1
        return True

    #
    # Get object count.  If first byte is 0x80 or higger it will tell
    #      bytes
    # count.
    # data received data.
    # Object count.
    #
    @classmethod
    def getObjectCount(cls, data):
        cnt = data.getUInt8()
        if cnt > 0x80:
            if cnt == 0x81:
                cnt = data.getUInt8()
            elif cnt == 0x82:
                cnt = data.getUInt16()
            elif cnt == 0x84:
                cnt = int(data.getUInt32())
            else:
                raise ValueError("Invalid count.")
        return cnt

    #
    # Return how many bytes object count takes.
    #
    # count
    # Value
    # Value size in bytes.
    #
    @classmethod
    def getObjectCountSizeInBytes(cls, count):
        if count < 0x80:
            ret = 1
        elif count < 0x100:
            ret = 2
        elif count < 0x10000:
            ret = 3
        else:
            ret = 5
        return ret

    #
    # Add string to byte buffer.
    #
    # value
    # String to add.
    # bb
    # Byte buffer where string is added.
    #
    @classmethod
    def addString(cls, value, bb):
        bb.setUInt8(DataType.OCTET_STRING)
        if not value:
            _GXCommon.setObjectCount(0, bb)
        else:
            _GXCommon.setObjectCount(len(value), bb)
            bb.set(value.encode())

    #
    # Set item count.
    # count
    # buff
    #
    @classmethod
    def setObjectCount(cls, count, buff):
        if count < 0x80:
            buff.setUInt8(count)
            ret = 1
        elif count < 0x100:
            buff.setUInt8(0x81)
            buff.setUInt8(count)
            ret = 2
        elif count < 0x10000:
            buff.setUInt8(0x82)
            buff.setUInt16(count)
            ret = 3
        else:
            buff.setUInt8(0x84)
            buff.setUInt32(count)
            ret = 5
        return ret

    #
    # Reserved for internal use.
    #
    @classmethod
    def toBitString(cls, value, count):
        count2 = count
        sb = ""
        if count2 > 0:
            count2 = min(count2, 8)
            pos = 7
            while pos != 8 - count2 - 1:
                if (value & (1 << pos)) != 0:
                    sb += '1'
                else:
                    sb += '0'
                pos -= 1
        return sb

    @classmethod
    def changeType(cls, settings, value, type_):
        #pylint: disable=import-outside-toplevel
        if value is None:
            ret = None
        elif type_ == DataType.NONE:
            ret = GXByteBuffer.hex(value, True)
        elif type_ in (DataType.STRING, DataType.OCTET_STRING) and not value:
            ret = ""
        elif type_ == DataType.OCTET_STRING:
            ret = GXByteBuffer(value)
        elif type_ == DataType.STRING and not GXByteBuffer.isAsciiString(value):
            ret = GXByteBuffer(value)
        elif type_ == DataType.DATETIME and not value:
            ret = GXDateTime(None)
        elif type_ == DataType.DATE and not value:
            ret = GXDate(None)
        elif type_ == DataType.TIME and not value:
            ret = GXTime(None)
        else:
            info = _GXDataInfo()
            info.type_ = type_
            ret = _GXCommon.getData(settings, GXByteBuffer(value), info)
            if not info.complete:
                raise ValueError("Change type failed. Not enought data.")
            if type_ == DataType.OCTET_STRING and isinstance(ret, bytes):
                ret = GXByteBuffer.hex(ret)
        return ret

    #
    # Get data from DLMS frame.
    #
    # data
    # received data.
    # info
    # Data info.
    # Received data.
    #
    @classmethod
    def getData(cls, settings, data, info):
        value = None
        startIndex = data.position
        if data.position == len(data):
            info.complete = False
            return None
        info.complete = True
        knownType = info.type_ != DataType.NONE
        #  Get data type if it is unknown.
        if not knownType:
            info.type_ = data.getUInt8()
        if info.type_ == DataType.NONE:
            if info.xml:
                info.xml.appendLine("<" + info.xml.getDataType(info.type_) + " />")
            return value
        if data.position == len(data):
            info.complete = False
            return None
        if info.type_ == DataType.ARRAY or info.type_ == DataType.STRUCTURE:
            value = cls.getArray(settings, data, info, startIndex)
        elif info.type_ == DataType.BOOLEAN:
            value = cls.getBoolean(data, info)
        elif info.type_ == DataType.BITSTRING:
            value = cls.getBitString(data, info)
        elif info.type_ == DataType.INT32:
            value = cls.getInt32(data, info)
        elif info.type_ == DataType.UINT32:
            value = cls.getUInt32(data, info)
        elif info.type_ == DataType.STRING:
            value = cls.getString(data, info, knownType)
        elif info.type_ == DataType.STRING_UTF8:
            value = cls.getUtfString(data, info, knownType)
        elif info.type_ == DataType.OCTET_STRING:
            value = cls.getOctetString(settings, data, info, knownType)
        elif info.type_ == DataType.BCD:
            value = cls.getBcd(data, info)
        elif info.type_ == DataType.INT8:
            value = cls.getInt8(data, info)
        elif info.type_ == DataType.INT16:
            value = cls.getInt16(data, info)
        elif info.type_ == DataType.UINT8:
            value = cls.getUInt8(data, info)
        elif info.type_ == DataType.UINT16:
            value = cls.getUInt16(data, info)
        elif info.type_ == DataType.COMPACT_ARRAY:
            value = cls.getCompactArray(settings, data, info)
        elif info.type_ == DataType.INT64:
            value = cls.getInt64(data, info)
        elif info.type_ == DataType.UINT64:
            value = cls.getUInt64(data, info)
        elif info.type_ == DataType.ENUM:
            value = cls.getEnum(data, info)
        elif info.type_ == DataType.FLOAT32:
            value = cls.getFloat(settings, data, info)
        elif info.type_ == DataType.FLOAT64:
            value = cls.getDouble(settings, data, info)
        elif info.type_ == DataType.DATETIME:
            value = cls.getDateTime(settings, data, info)
        elif info.type_ == DataType.DATE:
            value = cls.getDate(data, info)
        elif info.type_ == DataType.TIME:
            value = cls.getTime(data, info)
        else:
            raise ValueError("Invalid data type.")
        return value

    #
    # Convert value to hex string.
    # value value to convert.
    # desimals Amount of decimals.
    # @return
    #
    @classmethod
    def integerToHex(cls, value, desimals):
        if desimals:
            nbits = desimals * 4
            str_ = hex((value + (1 << nbits)) % (1 << nbits))[2:].upper()
        else:
            str_ = hex(value)[2:].upper()
        if not desimals or desimals == len(str_):
            return str_
        return _GXCommon.zeroes[0: desimals - len(str_)] + str_.upper()

    #
    # Convert value to hex string.
    # value value to convert.
    # desimals Amount of decimals.
    # @return
    #
    @classmethod
    def integerString(cls, value, desimals):
        str_ = str(value)
        if desimals == 0 or len(_GXCommon.zeroes) == len(str_):
            return str_
        return _GXCommon.zeroes[0: desimals - len(str_)] + str_

    #
    # Get array from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # index
    # starting index.
    # Object array.
    #
    @classmethod
    def getArray(cls, settings, buff, info, index):
        value = None
        if info.count == 0:
            info.count = _GXCommon.getObjectCount(buff)
        if info.xml:
            info.xml.appendStartTag(info.xml.getDataType(info.type_), "Qty", info.xml.integerToHex(info.count, 2))
        size = len(buff) - buff.position
        if info.count != 0 and size < 1:
            info.complete = False
            return None
        startIndex = index
        if info.type_ == DataType.ARRAY:
            value = GXArray()
        else:
            value = GXStructure()
        #  Position where last row was found.  Cache uses this info.
        pos = info.index
        while pos != info.count:
            info2 = _GXDataInfo()
            info2.xml = info.xml
            tmp = cls.getData(settings, buff, info2)
            if not info2.complete:
                buff.position = startIndex
                info.complete = False
                break
            if info2.count == info2.index:
                startIndex = buff.position
                value.append(tmp)
            pos += 1
        if info.xml:
            info.xml.appendEndTag(info.xml.getDataType(info.type_))
        info.index = pos
        return value

    #
    # Get time from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # Parsed time.
    #
    @classmethod
    def getTime(cls, buff, info):
        # pylint: disable=broad-except
        value = None
        if len(buff) - buff.position < 4:
            #  If there is not enough data available.
            info.complete = False
            return None
        str_ = None
        if info.xml:
            str_ = buff.toHex(False, buff.position, 4)
        try:
            value = GXTime(None)
            #  Get time.
            hour = buff.getUInt8()
            if hour == 0xFF:
                hour = 0
                value.skip |= DateTimeSkips.HOUR
            minute = buff.getUInt8()
            if minute == 0xFF:
                minute = 0
                value.skip |= DateTimeSkips.MINUTE
            second = buff.getUInt8()
            if second == 0xFF:
                second = 0
                value.skip |= DateTimeSkips.SECOND
            ms = buff.getUInt8()
            if ms != 0xFF:
                ms *= 10
            else:
                ms = 0
                value.skip |= DateTimeSkips.MILLISECOND
            value.value = datetime(1900, 1, 1, hour, minute, second, ms)
        except Exception as ex:
            if info.xml is None:
                raise ex
        if info.xml:
            if value:
                info.xml.appendComment(str(value))
            info.xml.appendLine(info.xml.getDataType(info.type_), None, str_)
        return value

    #
    # Get date from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # Parsed date.
    #
    @classmethod
    def getDate(cls, buff, info):
        # pylint: disable=broad-except
        value = None
        if len(buff) - buff.position < 5:
            #  If there is not enough data available.
            info.complete = False
            return None
        str_ = None
        if info.xml:
            str_ = buff.integerToHex(False, buff.position, 5)
        try:
            dt = GXDate()
            #  Get year.
            year = buff.getUInt16()
            if year < 1900 or year == 0xFFFF:
                dt.skip |= DateTimeSkips.YEAR
                year = 2000
            #  Get month
            month = buff.getUInt8()
            if month == 0xFE:
                dt.extra |= DateTimeExtraInfo.DST_BEGIN
                month = 1
            elif month == 0xFD:
                dt.extra |= DateTimeExtraInfo.DST_END
                month = 1
            else:
                if month < 1 or month > 12:
                    dt.skip |= DateTimeSkips.MONTH
                    month = 1
            #  Get day
            day = buff.getUInt8()
            if day == 0xFE:
                dt.extra |= DateTimeExtraInfo.LAST_DAY
                day = 1
            elif day == 0xFD:
                dt.extra |= DateTimeExtraInfo.LAST_DAY2
                day = 1
            else:
                if day < 1 or day > 31:
                    dt.skip |= DateTimeSkips.DAY
                    day = 1
            dt.value = datetime(year, month, day, 0, 0, 0, 0)
            value = dt
            #  Skip week day
            if buff.getUInt8() == 0xFF:
                dt.skip |= DateTimeSkips.DAY_OF_WEEK
        except Exception as ex:
            if info.xml is None:
                raise ex
        if info.xml:
            if value:
                info.xml.appendComment(str(value))
            info.xml.appendLine(info.xml.getDataType(info.type_), None, str_)
        return value

    #
    # Get date and time from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # Parsed date and time.
    #
    @classmethod
    def getDateTime(cls, settings, buff, info):
        # pylint: disable=too-many-locals, broad-except
        value = None
        skip = DateTimeSkips.NONE
        extra = DateTimeExtraInfo.NONE
        #  If there is not enough data available.
        if len(buff) - buff.position < 12:
            info.complete = False
            return None
        str_ = None
        if info.xml:
            str_ = buff.toHex(False, buff.position, 12)
        dt = GXDateTime()
        try:
            #  Get year.
            year = buff.getUInt16()
            #  Get month
            month = buff.getUInt8()
            #  Get day
            day = buff.getUInt8()
            #  Skip week day
            dayOfWeek = buff.getUInt8()
            if dayOfWeek == 0xFF:
                skip |= DateTimeSkips.DAY_OF_WEEK
            else:
                dt.dayOfWeek = dayOfWeek
            #  Get time.
            hour = buff.getUInt8()
            minute = buff.getUInt8()
            second = buff.getUInt8()
            ms = buff.getUInt8() & 0xFF
            if ms != 0xFF:
                ms *= 10
            else:
                ms = -1
            deviation = buff.getInt16()
            if deviation == -32768:
                deviation = 0x8000
                skip |= DateTimeSkips.DEVITATION
            status = buff.getUInt8()
            dt.status = status
            if year < 1900 or year == 0xFFFF:
                skip |= DateTimeSkips.YEAR
                year = 2000
            if month == 0xFE:
                extra |= DateTimeExtraInfo.DST_BEGIN
                month = 1
            elif month == 0xFD:
                extra |= DateTimeExtraInfo.DST_END
                month = 1
            else:
                if month < 1 or month > 12:
                    skip |= DateTimeSkips.MONTH
                    month = 1

            if day == 0xFE:
                extra |= DateTimeExtraInfo.LAST_DAY
                day = 1
            elif day == 0xFD:
                extra |= DateTimeExtraInfo.LAST_DAY2
                day = 1
            else:
                if day == -1 or day == 0 or day > 31:
                    skip |= DateTimeSkips.DAY
                    day = 1

            if hour < 0 or hour > 24:
                skip |= DateTimeSkips.HOUR
                hour = 0
            if minute < 0 or minute > 60:
                skip |= DateTimeSkips.MINUTE
                minute = 0
            if second < 0 or second > 60:
                skip |= DateTimeSkips.SECOND
                second = 0
            #  If ms is Zero it's skipped.
            if ms < 0 or ms > 100:
                skip |= DateTimeSkips.MILLISECOND
                ms = 0
            tz = None
            if deviation != 0x8000:
                if settings.useUtc2NormalTime:
                    tz = deviation
                else:
                    tz = -deviation
            if tz is None:
                dt.value = datetime(year, month, day, hour, minute, second, ms)
            else:
                dt.value = datetime(year, month, day, hour, minute, second, ms, tzinfo=GXTimeZone(tz))
            dt.skip = skip
            value = dt
        except Exception as ex:
            if info.xml is None:
                raise ex
        if info.xml:
            if dt.skip & DateTimeSkips.YEAR == 0 and value:
                info.xml.appendComment(str(value))
            info.xml.appendLine(info.xml.getDataType(info.type_), None, str_)
        return value

    #
    # Get double value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # Parsed double value.
    #
    @classmethod
    def getDouble(cls, settings, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 8:
            info.complete = False
            return None
        value = buff.getDouble()
        if info.xml:
            if info.xml.comments:
                info.xml.appendComment(('%f' % value).rstrip('0').rstrip('.'))
            tmp = GXByteBuffer()
            cls.setData(settings, tmp, DataType.FLOAT64, value)
            info.xml.appendLine(info.xml.getDataType(info.type_), None, tmp.toHex(False, 1, len(tmp) - 1))
        return GXFloat64(value)

    #
    # Get float value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # Parsed float value.
    #
    @classmethod
    def getFloat(cls, settings, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 4:
            info.complete = False
            return None
        value = buff.getFloat()
        if info.xml:
            if info.xml.comments:
                info.xml.appendComment(('%f' % value).rstrip('0').rstrip('.'))
            tmp = GXByteBuffer()
            cls.setData(settings, tmp, DataType.FLOAT32, value)
            info.xml.appendLine(info.xml.getDataType(info.type_), None, tmp.toHex(False, 1, len(tmp) - 1))
        return GXFloat32(value)

    #
    # Get enumeration value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed enumeration value.
    #
    @classmethod
    def getEnum(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 1:
            info.complete = False
            return None
        value = buff.getUInt8()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 2))
        return GXEnum(value)

    #
    # Get UInt64 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UInt64 value.
    #
    @classmethod
    def getUInt64(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 8:
            info.complete = False
            return None
        value = buff.getUInt64()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 16))
        return GXUInt64(value)

    #
    # Get Int64 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed Int64 value.
    #
    @classmethod
    def getInt64(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 8:
            info.complete = False
            return None
        value = buff.getInt64()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 16))
        return value

    #
    # Get UInt16 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UInt16 value.
    #
    @classmethod
    def getUInt16(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 2:
            info.complete = False
            return None
        value = buff.getUInt16()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 4))
        return GXUInt16(value)

    #pylint: disable=too-many-arguments
    @classmethod
    def getCompactArrayItem(cls, settings, buff, dt, list_, len_):
        if isinstance(dt, list):
            tmp2 = list()
            for it in dt:
                if isinstance(it, DataType):
                    cls.getCompactArrayItem(settings, buff, it, tmp2, 1)
                else:
                    cls.getCompactArrayItem(settings, buff, it, tmp2, 1)
            list_.append(tmp2)
            return

        tmp = _GXDataInfo()
        tmp.type_ = dt
        start = buff.position
        if dt == DataType.STRING:
            while buff.position - start < len_:
                tmp.clear()
                tmp.type = dt
                list_.append(cls.getString(buff, tmp, False))
                if not tmp.complete:
                    break
        elif dt == DataType.OCTET_STRING:
            while buff.position - start < len_:
                tmp.clear()
                tmp.type = dt
                list_.append(cls.getOctetString(settings, buff, tmp, False))
                if not tmp.complete:
                    break
        else:
            while buff.position - start < len_:
                tmp.clear()
                tmp.type_ = dt
                list_.append(cls.getData(settings, buff, tmp))
                if not tmp.complete:
                    break

    @classmethod
    def getDataTypes(cls, buff, cols, len_):
        dt = None
        pos = 0
        while pos != len_:
            dt = buff.getUInt8()
            if dt == DataType.ARRAY:
                cnt = buff.getUInt16()
                tmp = list()
                tmp2 = list()
                cls.getDataTypes(buff, tmp, 1)
                i = 0
                while i != cnt:
                    tmp2.append(tmp)
                    i += 1
                cols.append(tmp2)
            elif dt == DataType.STRUCTURE:
                tmp = list()
                cls.getDataTypes(buff, tmp, buff.getUInt8())
                cols.append(tmp)
            else:
                cols.append(dt)
            pos += 1

    @classmethod
    def appendDataTypeAsXml(cls, cols, info):
        for it in cols:
            if isinstance(it, (DataType,)):
                info.xml.appendEmptyTag(info.xml.getDataType(it))
            elif isinstance(it, GXStructure):
                info.xml.appendStartTag(cls.DATA_TYPE_OFFSET + DataType.STRUCTURE, None, None)
                cls.appendDataTypeAsXml(it, info)
                info.xml.appendEndTag(cls.DATA_TYPE_OFFSET + DataType.STRUCTURE)
            elif isinstance(it, GXArray):
                info.xml.appendStartTag(cls.DATA_TYPE_OFFSET + DataType.ARRAY, None, None)
                cls.appendDataTypeAsXml(it, info)
                info.xml.appendEndTag(cls.DATA_TYPE_OFFSET + DataType.ARRAY)

    #
    # Get compact array value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UInt16 value.
    #
    @classmethod
    def getCompactArray(cls, settings, buff, info):
        # pylint: disable=too-many-nested-blocks

        #  If there is not enough data available.
        if len(buff) - buff.position < 2:
            info.complete = False
            return None
        dt = buff.getUInt8()
        if dt == DataType.ARRAY:
            raise ValueError("Invalid compact array data.")
        len_ = _GXCommon.getObjectCount(buff)
        list_ = list()
        if dt == DataType.STRUCTURE:
            #  Get data types.
            cols = list()
            cls.getDataTypes(buff, cols, len_)
            len_ = _GXCommon.getObjectCount(buff)
            if info.xml:
                info.xml.appendStartTag(info.xml.getDataType(DataType.COMPACT_ARRAY), None, None)
                info.xml.appendStartTag(TranslatorTags.CONTENTS_DESCRIPTION)
                cls.appendDataTypeAsXml(cols, info)
                info.xml.appendEndTag(TranslatorTags.CONTENTS_DESCRIPTION)
                if info.xml.outputType == TranslatorOutputType.STANDARD_XML:
                    info.xml.appendStartTag(TranslatorTags.ARRAY_CONTENTS, None, None, True)
                    info.xml.append(buff.remainingHexString(True))
                    info.xml.appendEndTag(TranslatorTags.ARRAY_CONTENTS, True)
                    info.xml.appendEndTag(info.xml.getDataType(DataType.COMPACT_ARRAY))
                else:
                    info.xml.appendStartTag(TranslatorTags.ARRAY_CONTENTS)
            start = buff.position
            while buff.position - start < len_:
                row = list()
                pos = 0
                while pos != len(cols):
                    if isinstance(cols[pos], GXArray):
                        cls.getCompactArrayItem(settings, buff, cols[pos], row, 1)
                    elif isinstance(cols[pos], GXStructure):
                        tmp2 = list()
                        cls.getCompactArrayItem(settings, buff, cols[pos], tmp2, 1)
                        row.append(tmp2[0])
                    else:
                        cls.getCompactArrayItem(settings, buff, cols[pos], row, 1)
                    if buff.position == len(buff):
                        break
                    pos += 1
                #  If all columns are read.
                if len(row) >= len(cols):
                    list_.append(row)
                else:
                    break
            if info.xml and info.xml.outputType == TranslatorOutputType.SIMPLE_XML:
                sb = ""
                for row in list_:
                    for it in row:
                        if isinstance(it, bytearray):
                            sb += GXByteBuffer.hex(it)
                        elif isinstance(it, list):
                            start = len(sb)
                            for it2 in it:
                                if isinstance(it2, bytearray):
                                    sb += GXByteBuffer.hex(it2)
                                else:
                                    sb += str(it2)
                                sb += ";"
                            if start != len(sb):
                                sb = sb[0:len(sb) - 1]
                        else:
                            sb += str(it)
                        sb += ";"
                    if sb:
                        sb = sb[0:len(sb) - 1]
                    info.xml.appendLine(sb)
                    sb = ""
            if info.xml and info.xml.outputType == TranslatorOutputType.SIMPLE_XML:
                info.xml.appendEndTag(TranslatorTags.ARRAY_CONTENTS)
                info.xml.appendEndTag(info.xml.getDataType(DataType.COMPACT_ARRAY))
        else:
            if info.xml:
                info.xml.appendStartTag(info.xml.getDataType(DataType.COMPACT_ARRAY), None, None)
                info.xml.appendStartTag(TranslatorTags.CONTENTS_DESCRIPTION)
                info.xml.appendEmptyTag(info.xml.getDataType(dt))
                info.xml.appendEndTag(TranslatorTags.CONTENTS_DESCRIPTION)
                info.xml.appendStartTag(TranslatorTags.ARRAY_CONTENTS, None, None, True)
                if info.xml.outputType == TranslatorOutputType.STANDARD_XML:
                    info.xml.append(buff.remainingHexStringFalse)
                    info.xml.appendEndTag(TranslatorTags.ARRAY_CONTENTS, True)
                    info.xml.appendEndTag(info.xml.getDataType(DataType.COMPACT_ARRAY))
            cls.getCompactArrayItem(settings, buff, dt, list_, len_)
            if info.xml and info.xml.outputType == TranslatorOutputType.SIMPLE_XML:
                for it in list_:
                    if isinstance(it, bytearray):
                        info.xml.append(GXByteBuffer.hex(it))
                    else:
                        info.xml.append(str(it))
                    info.xml.append(";")
                if list_:
                    info.xml.setXmlLength(info.xml.getXmlLength() - 1)
                info.xml.appendEndTag(TranslatorTags.ARRAY_CONTENTS, True)
                info.xml.appendEndTag(info.xml.getDataType(DataType.COMPACT_ARRAY))
        return list_

    #
    # Get UInt8 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UInt8 value.
    #
    @classmethod
    def getUInt8(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 1:
            info.complete = False
            return None
        value = buff.getUInt8() & 0xFF
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 2))
        return GXUInt8(value)

    #
    # Get Int16 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed Int16 value.
    #
    @classmethod
    def getInt16(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 2:
            info.complete = False
            return None
        value = int(buff.getInt16())
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 4))
        return value

    #
    # Get Int8 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed Int8 value.
    #
    @classmethod
    def getInt8(cls, buff, info):
        value = None
        #  If there is not enough data available.
        if len(buff) - buff.position < 1:
            info.complete = False
            return None
        value = int(buff.getInt8())
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 2))
        return GXInt8(value)

    #
    # Get BCD value from DLMS data.
    #
    # buff: Received DLMS data.
    # info: Data info.
    # Returns parsed BCD value.
    #
    @classmethod
    def getBcd(cls, buff, info):
        #  If there is not enough data available.
        if len(buff) - buff.position < 1:
            info.complete = False
            return None
        value = buff.getUInt8()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 2))
        return value

    #
    # Get UTF string value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UTF string value.
    #
    @classmethod
    def getUtfString(cls, buff, info, knownType):
        if knownType:
            len_ = len(buff)
        else:
            len_ = _GXCommon.getObjectCount(buff)
            #  If there is not enough data available.
            if len(buff) - buff.position < len_:
                info.complete = False
                return None
        if len_ > 0:
            value = buff.getString(buff.position, len_)
            buff.position += len_
        else:
            value = ""
        if info.xml:
            if info.xml.getShowStringAsHex:
                info.xml.appendLine(info.xml.getDataType(info.type_), None, buff.toHex(False, buff.position - len, len))
            else:
                info.xml.appendLine(info.xml.getDataType(info.type_), None, value)
        return value

    #
    # Get octet string value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed octet string value.
    #
    @classmethod
    def getOctetString(cls, settings, buff, info, knownType):
        # pylint: disable=too-many-nested-blocks,broad-except
        value = None
        if knownType:
            len_ = len(buff)
        else:
            len_ = _GXCommon.getObjectCount(buff)
            #  If there is not enough data available.
            if len(buff) - buff.position < len_:
                info.complete = False
                return None
        tmp = bytearray(len_)
        buff.get(tmp)
        value = tmp
        if info.xml:
            if info.xml.comments and tmp:
                #  This might be a logical name.
                if len(tmp) == 6 and tmp[5] == 255:
                    info.xml.appendComment(cls.toLogicalName(tmp))
                else:
                    isString = True
                    #  Try to move octect string to DateTime, Date or time.
                    if len(tmp) == 12 or len(tmp) == 5 or len(tmp) == 4:
                        try:
                            type_ = None
                            if len(tmp) == 12:
                                type_ = DataType.DATETIME
                            elif len(tmp) == 5:
                                type_ = DataType.DATE
                            else:
                                type_ = DataType.TIME
                            dt = _GXCommon.changeType(settings, tmp, type_)
                            year = dt.value.year
                            if 1970 < year < 2100:
                                info.xml.appendComment(str(dt))
                                isString = False
                        except Exception:
                            isString = True
                    if isString:
                        for it in tmp:
                            if it < 32 or it > 126:
                                isString = False
                                break
                        if isString:
                            info.xml.appendComment(str(tmp))
            info.xml.appendLine(info.xml.getDataType(info.type_), None, GXByteBuffer.hex(tmp, False))
        return value

    #
    # Get string value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed string value.
    #
    @classmethod
    def getString(cls, buff, info, knownType):
        value = None
        if knownType:
            len_ = len(buff)
        else:
            len_ = _GXCommon.getObjectCount(buff)
            #  If there is not enough data available.
            if len(buff) - buff.position < len_:
                info.complete = False
                return None
        if len_ > 0:
            value = buff.getString(buff.position, len_)
            buff.position += len_
        else:
            value = ""
        if info.xml:
            if info.xml.showStringAsHex:
                info.xml.appendLine(info.xml.getDataType(info.type_), None, buff.toHex(False, buff.position - len_, len_))
            else:
                info.xml.appendLine(info.xml.getDataType(info.type_), None, value)
        return value

    #
    # Get UInt32 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed UInt32 value.
    #
    @classmethod
    def getUInt32(cls, buff, info):
        #  If there is not enough data available.
        if len(buff) - buff.position < 4:
            info.complete = False
            return None
        value = buff.getUInt32()
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 8))
        return GXUInt32(value)

    #
    # Get Int32 value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed Int32 value.
    #
    @classmethod
    def getInt32(cls, buff, info):
        #  If there is not enough data available.
        if len(buff) - buff.position < 4:
            info.complete = False
            return None
        value = int(buff.getInt32())
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, info.xml.integerToHex(value, 8))
        return value

    #
    # Get bit string value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed bit string value.
    #
    @classmethod
    def getBitString(cls, buff, info):
        cnt = cls.getObjectCount(buff)
        t = cnt
        t /= 8
        if cnt % 8 != 0:
            t += 1
        byteCnt = int(t)
        #  If there is not enough data available.
        if len(buff) - buff.position < byteCnt:
            info.complete = False
            return None
        sb = ""
        while cnt > 0:
            sb += cls.toBitString(buff.getInt8(), cnt)
            cnt -= 8
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, sb)
        return GXBitString(sb)

    #
    # Get boolean value from DLMS data.
    #
    # buff
    # Received DLMS data.
    # info
    # Data info.
    # parsed boolean value.
    #
    @classmethod
    def getBoolean(cls, buff, info):
        #  If there is not enough data available.
        if len(buff) - buff.position < 1:
            info.complete = False
            return None
        value = bool(buff.getUInt8() != 0)
        if info.xml:
            info.xml.appendLine(info.xml.getDataType(info.type_), None, value.__str__())
        return value

    #
    # Get HDLC address from byte array.
    #
    # buff
    # byte array.
    # HDLC address.
    #
    @classmethod
    def getHDLCAddress(cls, buff):
        size = 0
        pos = buff.position
        while pos != len(buff):
            size += 1
            if buff.getUInt8(pos) & 0x1 == 1:
                break
            pos += 1
        if size == 1:
            ret = (buff.getUInt8() & 0xFE) >> 1
        elif size == 2:
            ret = buff.getUInt16()
            ret = ((ret & 0xFE) >> 1) | ((ret & 0xFE00) >> 2)
        elif size == 4:
            ret = buff.getUInt32()
            ret = ((ret & 0xFE) >> 1) | ((ret & 0xFE00) >> 2) | ((ret & 0xFE0000) >> 3) | ((ret & 0xFE000000) >> 4)
        else:
            raise ValueError("Wrong size.")
        return ret

    #
    # Convert object to DLMS bytes.
    #
    # settings: DLMS settings.
    # buff: Byte buffer where data is write.
    # dataType: Data type.
    # value: Added Value.
    #
    @classmethod
    def setData(cls, settings, buff, dataType, value):
        if dataType in (DataType.ARRAY, DataType.STRUCTURE) and isinstance(value, (GXByteBuffer, bytearray, bytes)):
            #  If byte array is added do not add type.
            buff.set(value)
            return

        buff.setUInt8(dataType)
        if dataType == DataType.NONE:
            pass
        elif dataType == DataType.BOOLEAN:
            if value:
                buff.setUInt8(1)
            else:
                buff.setUInt8(0)
        elif dataType == DataType.UINT8:
            buff.setUInt8(value)
        elif dataType in (DataType.INT8, DataType.ENUM):
            buff.setInt8(value)
        elif dataType in (DataType.UINT16, DataType.INT16):
            buff.setUInt16(value)
        elif dataType in (DataType.UINT32, DataType.INT32):
            buff.setUInt32(value)
        elif dataType in (DataType.UINT64, DataType.INT64):
            buff.setUInt64(value)
        elif dataType == DataType.FLOAT32:
            buff.setFloat(value)
        elif dataType == DataType.FLOAT64:
            buff.setDouble(value)
        elif dataType == DataType.BITSTRING:
            cls.setBitString(buff, value, True)
        elif dataType == DataType.STRING:
            cls.setString(buff, value)
        elif dataType == DataType.STRING_UTF8:
            cls.setUtfString(buff, value)
        elif dataType == DataType.OCTET_STRING:
            if isinstance(value, GXDate):
                #  Add size
                buff.setUInt8(5)
                cls.setDate(buff, value)
            elif isinstance(value, GXTime):
                #  Add size
                buff.setUInt8(4)
                cls.setTime(buff, value)
            elif isinstance(value, (GXDateTime, datetime)):
                buff.setUInt8(12)
                cls.setDateTime(settings, buff, value)
            else:
                cls.setOctetString(buff, value)
        elif dataType in (DataType.ARRAY, DataType.STRUCTURE):
            cls.setArray(settings, buff, value)
        elif dataType == DataType.BCD:
            cls.setBcd(buff, value)
        elif dataType == DataType.COMPACT_ARRAY:
            #  Compact array is not work with python because we don't know data
            #  types of each element.
            raise ValueError("Invalid data type.")
        elif dataType == DataType.DATETIME:
            cls.setDateTime(settings, buff, value)
        elif dataType == DataType.DATE:
            cls.setDate(buff, value)
        elif dataType == DataType.TIME:
            cls.setTime(buff, value)
        else:
            raise ValueError("Invalid data type.")

    #
    # Convert time to DLMS bytes.
    #
    # buff
    # Byte buffer where data is write.
    # value
    # Added value.
    #
    @classmethod
    def setTime(cls, buff, value):
        dt = _GXCommon.__getDateTime(value)
        #  Add time.
        if dt.skip & DateTimeSkips.HOUR != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.hour)
        if dt.skip & DateTimeSkips.MINUTE != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.minute)
        if dt.skip & DateTimeSkips.SECOND != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.second)
        if dt.skip & DateTimeSkips.MILLISECOND != DateTimeSkips.NONE:
            #  Hundredth of seconds is not used.
            buff.setUInt8(0xFF)
        else:
            ms = dt.value.microsecond
            if ms != 0:
                ms /= 10000
            buff.setUInt8(int(ms))

    #
    # Convert date to DLMS bytes.
    #
    # buff
    # Byte buffer where data is write.
    # value
    # Added value.
    #
    @classmethod
    def setDate(cls, buff, value):
        dt = _GXCommon.__getDateTime(value)
        #  Add year.
        if dt.skip & DateTimeSkips.YEAR != DateTimeSkips.NONE:
            buff.setUInt16(0xFFFF)
        else:
            buff.setUInt16(dt.value.year)
        #  Add month
        if dt.extra & DateTimeExtraInfo.DST_BEGIN != 0:
            buff.setUInt8(0xFE)
        elif dt.extra & DateTimeExtraInfo.DST_END != 0:
            buff.setUInt8(0xFD)
        elif dt.skip & DateTimeSkips.MONTH != 0:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.month)
        #  Add day
        if dt.extra & DateTimeExtraInfo.LAST_DAY2 != DateTimeSkips.NONE:
            buff.setUInt8(0xFD)
        elif dt.extra & DateTimeExtraInfo.LAST_DAY != DateTimeSkips.NONE:
            buff.setUInt8(0xFE)
        elif dt.skip & DateTimeSkips.DAY != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.day)

        #  Day of week.
        if dt.skip & DateTimeSkips.DAY_OF_WEEK != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            if dt.dayOfWeek == 0:
                buff.setUInt8(dt.value.weekday() + 1)
            else:
                buff.setUInt8(dt.dayOfWeek)

    @classmethod
    def __getDateTime(cls, value):
        dt = None
        if isinstance(value, (GXDateTime)):
            dt = value
        elif isinstance(value, (datetime, str)):
            dt = GXDateTime(value)
            dt.skip |= DateTimeSkips.MILLISECOND
        else:
            raise ValueError("Invalid date format.")
        return dt

    #
    # Convert date time to DLMS bytes.
    #
    # buff
    # Byte buffer where data is write.
    # value
    # Added value.
    #
    @classmethod
    def setDateTime(cls, settings, buff, value):
        dt = cls.__getDateTime(value)
        skip = dt.skip
        if settings and settings.dateTimeSkips:
            skip = skip or settings.dateTimeSkips

        #  Add year.
        if skip & DateTimeSkips.YEAR != DateTimeSkips.NONE:
            buff.setUInt16(0xFFFF)
        else:
            buff.setUInt16(dt.value.year)
        #  Add month
        if dt.extra & DateTimeExtraInfo.DST_BEGIN != 0:
            buff.setUInt8(0xFD)
        elif dt.extra & DateTimeExtraInfo.DST_END != 0:
            buff.setUInt8(0xFE)
        elif skip & DateTimeSkips.MONTH != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.month)

        #  Add day
        if dt.extra & DateTimeExtraInfo.LAST_DAY2 != DateTimeSkips.NONE:
            buff.setUInt8(0xFD)
        elif dt.extra & DateTimeExtraInfo.LAST_DAY != DateTimeSkips.NONE:
            buff.setUInt8(0xFE)
        elif skip & DateTimeSkips.DAY != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.day)
        #  Day of week.
        if skip & DateTimeSkips.DAY_OF_WEEK != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            if dt.dayOfWeek == 0:
                buff.setUInt8(dt.value.weekday() + 1)
            else:
                buff.setUInt8(dt.dayOfWeek)
        #  Add time.
        if skip & DateTimeSkips.HOUR != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.hour)
        if skip & DateTimeSkips.MINUTE != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.minute)
        if skip & DateTimeSkips.SECOND != DateTimeSkips.NONE:
            buff.setUInt8(0xFF)
        else:
            buff.setUInt8(dt.value.second)
        if skip & DateTimeSkips.MILLISECOND != DateTimeSkips.NONE:
            #  Hundredth of seconds is not used.
            buff.setUInt8(0xFF)
        else:
            ms = dt.value.microsecond
            if ms != 0:
                ms /= 10000
            buff.setUInt8(int(ms))
        #  devitation not used.
        if skip & DateTimeSkips.DEVITATION != DateTimeSkips.NONE:
            buff.setUInt16(0x8000)
        else:
            #  Add devitation.
            d = int(dt.value.utcoffset().seconds / 60)
            if not (settings and settings.useUtc2NormalTime):
                d = -d
            buff.setUInt16(d)
        #  Add clock_status
        if skip & DateTimeSkips.STATUS == DateTimeSkips.NONE:
            if dt.value.dst() or dt.status & ClockStatus.DAYLIGHT_SAVE_ACTIVE != ClockStatus.OK:
                buff.setUInt8(dt.status | ClockStatus.DAYLIGHT_SAVE_ACTIVE)
            else:
                buff.setUInt8(dt.status)
        else:
            buff.setUInt8(0xFF)

    @classmethod
    def setBcd(cls, buff, value):
        buff.setUInt8(value)

    @classmethod
    def setArray(cls, settings, buff, value):
        if value:
            _GXCommon.setObjectCount(len(value), buff)
            for it in value:
                cls.setData(settings, buff, cls.getDLMSDataType(it), it)
        else:
            _GXCommon.setObjectCount(0, buff)

    @classmethod
    def setOctetString(cls, buff, value):
        if isinstance(value, str):
            tmp = GXByteBuffer.hexToBytes(value)
            _GXCommon.setObjectCount(len(tmp), buff)
            buff.set(tmp)
        elif isinstance(value, GXByteBuffer):
            cls.setObjectCount(len(value), buff)
            buff.set(value)
        elif isinstance(value, (bytearray, bytes)):
            cls.setObjectCount(len(value), buff)
            buff.set(value)
        elif value is None:
            cls.setObjectCount(0, buff)
        else:
            raise ValueError("Invalid data type.")

    @classmethod
    def setUtfString(cls, buff, value):
        if value:
            tmp = value.encode()
            _GXCommon.setObjectCount(len(tmp), buff)
            buff.set(tmp)
        else:
            buff.setUInt8(0)

    @classmethod
    def setString(cls, buff, value):
        if value:
            _GXCommon.setObjectCount(len(value), buff)
            buff.set(_GXCommon.getBytes(value))
        else:
            buff.setUInt8(0)

    @classmethod
    def setBitString(cls, buff, val1, addCount):
        value = val1
        if isinstance(value, GXBitString):
            value = value.value
        if isinstance(value, str):
            val = 0
            str_ = str(value)
            if addCount:
                _GXCommon.setObjectCount(len(str_), buff)
            index = 7
            pos = 0
            while pos != len(str_):
                it = str_[pos]
                if it == '1':
                    val |= (1 << index)
                elif it != '0':
                    raise ValueError("Not a bit string.")
                index -= 1
                if index == -1:
                    index = 7
                    buff.setUInt8(val)
                    val = 0
                pos += 1
            if index != 7:
                buff.setUInt8(val)
        elif isinstance(value, (bytearray, bytes)):
            _GXCommon.setObjectCount(8 * len(value), buff)
            buff.set(value)
        elif isinstance(value, int):
            _GXCommon.setObjectCount(8, buff)
            buff.setUInt8(value)
        elif value is None:
            buff.setUInt8(0)
        else:
            raise ValueError("BitString must give as string.")

    @classmethod
    def getDataType(cls, value):
        if value == DataType.NONE:
            ret = None
        elif value == DataType.OCTET_STRING:
            ret = bytes.__class__
        elif value == DataType.ENUM:
            ret = GXEnum.__class__
        elif value == DataType.INT8:
            ret = int.__class__
        elif value == DataType.INT16:
            ret = int.__class__
        elif value == DataType.INT32:
            ret = int.__class__
        elif value == DataType.INT64:
            ret = int.__class__
        elif value == DataType.UINT8:
            ret = GXUInt8.__class__
        elif value == DataType.UINT16:
            ret = GXUInt16.__class__
        elif value == DataType.UINT32:
            ret = GXUInt32.__class__
        elif value == DataType.UINT64:
            ret = GXUInt64.__class__
        elif value == DataType.TIME:
            ret = GXTime.__class__
        elif value == DataType.DATE:
            ret = GXDate.__class__
        elif value == DataType.DATETIME:
            ret = GXDateTime.__class__
        elif value == DataType.ARRAY:
            ret = list.__class__
        elif value == DataType.STRING:
            ret = str.__class__
        elif value == DataType.BOOLEAN:
            ret = bool.__class__
        elif value == DataType.FLOAT32:
            ret = GXFloat32.__class__
        elif value == DataType.FLOAT64:
            ret = GXFloat64.__class__
        elif value == DataType.BITSTRING:
            ret = GXBitString.__class__
        else:
            raise ValueError("Invalid value.")
        return ret

    @classmethod
    def getDLMSDataType(cls, value):
        # pylint: disable=undefined-variable
        if value is None:
            ret = DataType.NONE
        elif isinstance(value, (bytes, bytearray, GXByteBuffer)):
            ret = DataType.OCTET_STRING
        elif isinstance(value, (GXEnum)):
            ret = DataType.ENUM
        elif isinstance(value, (GXInt8)):
            ret = DataType.INT8
        elif isinstance(value, (GXInt16)):
            ret = DataType.INT16
        elif isinstance(value, (GXInt64)):
            ret = DataType.INT64
        elif isinstance(value, (GXUInt8)):
            ret = DataType.UINT8
        elif isinstance(value, (GXUInt16)):
            ret = DataType.UINT16
        elif isinstance(value, (GXUInt32)):
            ret = DataType.UINT32
        elif isinstance(value, (GXUInt64)):
            ret = DataType.UINT64
        elif isinstance(value, (bool)):
            ret = DataType.BOOLEAN
        elif isinstance(value, (GXInt32, int)):
            ret = DataType.INT32
        elif isinstance(value, (GXTime)):
            ret = DataType.TIME
        elif isinstance(value, (GXDate)):
            ret = DataType.DATE
        elif isinstance(value, (datetime, GXDateTime)):
            ret = DataType.DATETIME
        elif isinstance(value, (GXStructure)):
            ret = DataType.STRUCTURE
        elif isinstance(value, (GXArray, list)):
            ret = DataType.ARRAY
        elif isinstance(value, (str)):
            ret = DataType.STRING
        elif isinstance(value, (GXFloat64)):
            ret = DataType.FLOAT64
        elif isinstance(value, (GXFloat32, complex, float)):
            ret = DataType.FLOAT32
        elif isinstance(value, (GXBitString)):
            ret = DataType.BITSTRING
        else:
            ret = None
        if ret is None:
            #Python 2.7 uses unicode.
            try:
                if isinstance(value, (unicode)):
                    ret = DataType.STRING
            except Exception:
                ret = None
            if ret is None:
                raise ValueError("Invalid datatype " + type(value) + ".")
        return ret

    @classmethod
    def getDataTypeSize(cls, type_):
        size = -1
        if type_ == DataType.BCD:
            size = 1
        elif type_ == DataType.BOOLEAN:
            size = 1
        elif type_ == DataType.DATE:
            size = 5
        elif type_ == DataType.DATETIME:
            size = 12
        elif type_ == DataType.ENUM:
            size = 1
        elif type_ == DataType.FLOAT32:
            size = 4
        elif type_ == DataType.FLOAT64:
            size = 8
        elif type_ == DataType.INT16:
            size = 2
        elif type_ == DataType.INT32:
            size = 4
        elif type_ == DataType.INT64:
            size = 8
        elif type_ == DataType.INT8:
            size = 1
        elif type_ == DataType.NONE:
            size = 0
        elif type_ == DataType.TIME:
            size = 4
        elif type_ == DataType.UINT16:
            size = 2
        elif type_ == DataType.UINT32:
            size = 4
        elif type_ == DataType.UINT64:
            size = 8
        elif type_ == DataType.UINT8:
            size = 1
        return size

    @classmethod
    def toLogicalName(cls, value):
        if isinstance(value, bytearray):
            if not value:
                value = bytearray(6)
            if len(value) == 6:
                return str(value[0]) + "." + str(value[1]) + "." + str(value[2]) + "." + str(value[3]) + "." + str(value[4]) + "." + str(value[5])
            raise ValueError("Invalid Logical name.")
        return str(value)

    @classmethod
    def logicalNameToBytes(cls, value):
        if not value:
            return bytearray(6)
        items = value.split('.')
        if len(items) != 6:
            raise ValueError("Invalid Logical name.")
        buff = bytearray(6)
        pos = 0
        for it in items:
            v = int(it)
            if v < 0 or v > 255:
                raise ValueError("Invalid Logical name.")
            buff[pos] = int(v)
            pos += 1
        return buff

    @classmethod
    def getGeneralizedTime(cls, dateString):
        year = int(dateString[0:4])
        month = int(dateString[4:6])
        day = int(dateString[6:8])
        hour = int(dateString[8:10])
        minute = int(dateString[10:12])
        #If UTC time.
        if dateString.endsWith("Z"):
            if len(dateString) > 13:
                second = int(dateString[12:14])
            return datetime(year, month, day, hour, minute, second, 0, tzinfo=GXTimeZone(0))

        if len(dateString) > 17:
            second = int(dateString.substring(12, 14))
        tz = dateString[dateString.length() - 4:]
        return datetime(year, month, day, hour, minute, second, 0, tzinfo=GXTimeZone(tz))

    @classmethod
    def generalizedTime(cls, value):
        #Convert to UTC time.
        if isinstance(value, (GXDateTime)):
            value = value.value
        value = value.utctimetuple()
        sb = cls.integerString(value.tm_year, 4)
        sb += cls.integerString(value.tm_mon, 2)
        sb += cls.integerString(value.tm_mday, 2)
        sb += cls.integerString(value.tm_hour, 2)
        sb += cls.integerString(value.tm_min, 2)
        sb += cls.integerString(value.tm_sec, 2)
        #UTC time.
        sb += "Z"
        return sb

    @classmethod
    def encryptManufacturer(cls, flagName):
        if len(flagName) != 3:
            raise ValueError("Invalid Flag name.")
        value = (flagName.charAt(0) - 0x40) & 0x1f
        value <<= 5
        value += (flagName.charAt(0) - 0x40) & 0x1f
        value <<= 5
        value += ((flagName.charAt(0) - 0x40) & 0x1f)
        return value

    @classmethod
    def decryptManufacturer(cls, value):
        tmp = value >> 8 | value << 8
        c = chr(((tmp & 0x1f) + 0x40))
        tmp = tmp >> 5
        c1 = chr(((tmp & 0x1f) + 0x40))
        tmp = tmp >> 5
        c2 = chr(((tmp & 0x1f) + 0x40))
        return "".join([c2, c1, c])

    @classmethod
    def idisSystemTitleToString(cls, st):
        sb = '\n'
        sb += "IDIS system title:\n"
        sb += "Manufacturer Code: "
        sb += _GXCommon.__getChar(st[0]) + _GXCommon.__getChar(st[1]) + _GXCommon.__getChar(st[2])
        sb += "\nFunction type: "
        ft = st[4] >> 4
        add = False
        if (ft & 0x1) != 0:
            sb += "Disconnector extension"
            add = True
        if (ft & 0x2) != 0:
            if add:
                sb += ", "
            add = True
            sb += "Load Management extension"

        if (ft & 0x4) != 0:
            if add:
                sb += ", "
            sb += "Multi Utility extension"
        #Serial number
        sn = (st[4] & 0xF) << 24
        sn |= st[5] << 16
        sn |= st[6] << 8
        sn |= st[7]
        sb += '\n'
        sb += "Serial number: "
        sb += str(sn) + '\n'
        return sb

    @classmethod
    def dlmsSystemTitleToString(cls, st):
        sb = '\n'
        sb += "IDIS system title:\n"
        sb += "Manufacturer Code: "
        sb += _GXCommon.__getChar(st[0]) + _GXCommon.__getChar(st[1]) + _GXCommon.__getChar(st[2])
        sb += "Serial number: "
        sb += cls.__getChar(st[3]) + cls.__getChar(st[4]) + cls.__getChar(st[5]) + cls.__getChar(st[6]) + cls.__getChar(st[7])
        return sb

    @classmethod
    def uniSystemTitleToString(cls, st):
        sb = '\n'
        sb += "UNI/TS system title:\n"
        sb += "Manufacturer: "
        m = st[0] << 8 | st[1]
        sb += cls.decryptManufacturer(m)
        sb += "\nSerial number: "
        sb += GXByteBuffer.hex((st[7], st[6], st[5], st[4], st[3], st[2]), False)
        return sb

    @classmethod
    def __getChar(cls, ch):
        try:
            return str(chr(ch))
        except Exception:
            #If python 2.7 is used.
            #pylint: disable=undefined-variable
            return str(unichr(ch))

    @classmethod
    def systemTitleToString(cls, standard, st):
        ###Conver system title to string.
        #pylint: disable=too-many-boolean-expressions
        if standard == Standard.ITALY or not _GXCommon.__getChar(st[0]).isalpha() or \
            not cls.__getChar(st[1]).isalpha() or not cls.__getChar(st[2]).isalpha():
            return cls.uniSystemTitleToString(st)
        if standard == Standard.IDIS or not _GXCommon.__getChar(st[3]).isdigit() or \
            not _GXCommon.__getChar(st[4]).isdigit() or not _GXCommon.__getChar(st[5]).isdigit() or \
            not _GXCommon.__getChar(st[6]).isdigit() or not _GXCommon.__getChar(st[7]).isdigit():
            return cls.idisSystemTitleToString(st)
        return cls.dlmsSystemTitleToString(st)

    #Reserved for internal use.
    @classmethod
    def swapBits(cls, value):
        ret = 0
        pos = 0
        while pos != 8:
            ret = ret << 1 | value & 0x01
            value = value >> 1
            pos = pos + 1
        return ret
# from .enums.Command import Command

#pylint: disable=too-many-instance-attributes,too-many-public-methods
class GXDLMSChippering:

    #
    #      * Get nonse from frame counter and system title.
    #      * @param invocationCounter Invocation counter.
    #      * @param systemTitle System title.
    #      * @return Generated nonse.
    #
    @classmethod
    def getNonse(cls, invocationCounter, systemTitle):
        nonce = bytearray(12)
        nonce[0:8] = systemTitle
        nonce[8] = (invocationCounter >> 24) & 0xFF
        nonce[9] = (invocationCounter >> 16) & 0xFF
        nonce[10] = (invocationCounter >> 8) & 0xFF
        nonce[11] = invocationCounter & 0xFF
        return nonce
# 3bde7bdad68a3aca3c5f82939d32
# 0f5a3fccd68bb59cdbb15ca7
    @classmethod
    def encryptAesGcm(self,plainText,aad,iv,ciphertext):
        print("plainText"+str(plainText))
        # print("cls"+str(cls))
        # print("p"+str(p))

        countTag = None
        data = GXByteBuffer()
        data = 30
        tmp = bytearray(4)
        # invocationCounter = 0
        invocationCounter = 410
        tmp[0] = (invocationCounter >> 24) & 0xFF
        tmp[1] = (invocationCounter >> 16) & 0xFF
        tmp[2] = (invocationCounter >> 8) & 0xFF
        tmp[3] = invocationCounter & 0xFF

        # aad =  #getauthentication
        # iv = (b'qwertyui\x00\x00\x01\xac') #cls.getNonse(invocationCounter, p.systemTitle)
        # print(p.security)
        # print(p.blockCipherKey)
        print(aad)
        print(iv)
        security = Security.AUTHENTICATION_ENCRYPTION
        # ciphertext = b'34e7f5a8b9b5abd7f6cd32e5f18614'
        gcm = GXDLMSChipperingStream(security, True, blockCipherKey, aad, iv, None)
        
        print(gcm)
        print("hii")
        gcm.write(plainText)
        # print(gcm.tag)
        ciphertext = gcm.flushFinalBlock()
        print(ciphertext)
        return ciphertext
        # print(gcm.tag)
        print("hhi")
        # CountType.PACKET:
        print(tmp)
        # data.set(tmp)
        print(data)
        # if (p.type_ & CountType.DATA) != 0:
        #     print("hello")
        #     data.set(ciphertext)
        #     print(data)
        # if (p.type_ & CountType.TAG) != 0:
        #     print("hello2")
        #     p
        countTag = gcm.tag
        # data.set(p.countTag)
        print(data)
            # print(data)
        # else:
        #     raise ValueError("security")
        # if p.type_ == CountType.PACKET:
        #     tmp2 = GXByteBuffer(10 + len(data))
        #     tmp2.setUInt8(p.tag)
        #     if p.tag == Command.GENERAL_GLO_CIPHERING or p.tag == Command.GENERAL_DED_CIPHERING or p.tag == Command.DATA_NOTIFICATION:
        #         if not p.ignoreSystemTitle:
        #             _GXCommon.setObjectCount(len(p.systemTitle), tmp2)
        #             tmp2.set(p.systemTitle)
        #         else:
        #             tmp2.setUInt8(0)
        #     _GXCommon.setObjectCount(len(data), tmp2)
        #     tmp2.set(data, 0, len(data))
        #     data = tmp2
        crypted = data.array()
        print(crypted)
        return crypted

    @classmethod
    def getAuthenticatedData(cls, p, plainText):
        data = GXByteBuffer()
        sc = p.security | p.securitySuite
        if p.security == Security.AUTHENTICATION:
            data.setUInt8(sc)
            data.set(p.authenticationKey)
            data.set(plainText)
        elif p.security == Security.AUTHENTICATION_ENCRYPTION:
            data.setUInt8(sc)
            data.set(p.authenticationKey)
            if p.securitySuite != SecuritySuite.AES_GCM_128:
                #  transaction-id
                transactionId = GXByteBuffer()
                transactionId.setUInt64(p.invocationCounter)
                data.setUInt8(8)
                data.set(transactionId)
                #  originator-system-title
                _GXCommon.setObjectCount(len(p.systemTitle), data)
                data.set(p.systemTitle)
                #  recipient-system-title
                _GXCommon.setObjectCount(len(p.recipientSystemTitle), data)
                data.set(p.recipientSystemTitle)
                #  date-time not present
                data.setUInt8(0)
                #  other-information not present
                data.setUInt8(0)
        elif p.security == Security.ENCRYPTION:
            data.set(p.authenticationKey)
        return data.array()

    #
    #      * Decrypt data.
    #      *
    #      * @param c
    #      * Cipher settings.
    #      * @param p
    #      * GMAC Parameter.
    #      * @return Encrypted data.
    #
    @classmethod
    def decryptAesGcm(cls, p, data):
        # pylint: disable=too-many-locals
        if not data or len(data) - data.position < 2:
            raise ValueError("cryptedData")
        tmp = []
        len_ = 0
        cmd = data.getUInt8()
        if cmd in (Command.GENERAL_GLO_CIPHERING, Command.GENERAL_DED_CIPHERING):
            len_ = _GXCommon.getObjectCount(data)
            if len_ != 0:
                title = bytearray(len_)
                data.get(title)
                p.systemTitle = title
                if p.xml and p.xml.comments:
                    p.xml.appendComment(_GXCommon.systemTitleToString(0, p.systemTitle))
        elif cmd in (Command.GENERAL_CIPHERING, Command.GLO_INITIATE_REQUEST, Command.GLO_INITIATE_RESPONSE, Command.GLO_READ_REQUEST, Command.GLO_READ_RESPONSE, \
            Command.GLO_WRITE_REQUEST, Command.GLO_WRITE_RESPONSE, Command.GLO_GET_REQUEST, Command.GLO_GET_RESPONSE, Command.GLO_SET_REQUEST, \
            Command.GLO_SET_RESPONSE, Command.GLO_METHOD_REQUEST, Command.GLO_METHOD_RESPONSE, Command.GLO_EVENT_NOTIFICATION,\
            Command.DED_GET_REQUEST, Command.DED_GET_RESPONSE, Command.DED_SET_REQUEST, Command.DED_SET_RESPONSE, Command.DED_METHOD_REQUEST,\
            Command.DED_METHOD_RESPONSE, Command.DED_EVENT_NOTIFICATION, Command.DED_READ_REQUEST, Command.DED_READ_RESPONSE, Command.DED_WRITE_REQUEST, \
            Command.DED_WRITE_RESPONSE, Command.GLO_CONFIRMED_SERVICE_ERROR, Command.DED_CONFIRMED_SERVICE_ERROR):
            pass
        else:
            raise ValueError("cryptedData")
        value = 0
        transactionId = 0
        if cmd == Command.GENERAL_CIPHERING:
            len_ = _GXCommon.getObjectCount(data)
            tmp = bytearray(len_)
            data.get(tmp)
            t = GXByteBuffer(tmp)
            transactionId = t.getInt64()
            len_ = _GXCommon.getObjectCount(data)
            tmp = bytearray(len_)
            data.get(tmp)
            p.setSystemTitle(tmp)
            len_ = _GXCommon.getObjectCount(data)
            tmp = bytearray(len_)
            data.get(tmp)
            p.setRecipientSystemTitle(tmp)
            #  Get date time.
            len_ = _GXCommon.getObjectCount(data)
            if len_ != 0:
                tmp = bytearray(len_)
                data.get(tmp)
                p.dateTime = tmp
            #  other-information
            len_ = data.getUInt8()
            if len_ != 0:
                tmp = bytearray(len_)
                data.get(tmp)
                p.otherInformation = tmp
            #  KeyInfo OPTIONAL
            len_ = data.getUInt8()
            #  AgreedKey CHOICE tag.
            data.getUInt8()
            #  key-parameters
            len_ = data.getUInt8()
            value = data.getUInt8()
            p.setKeyParameters(value)
            if value == 1:
                #  KeyAgreement.ONE_PASS_DIFFIE_HELLMAN
                #  key-ciphered-data
                len_ = _GXCommon.getObjectCount(data)
                tmp = bytearray(len_)
                data.get(tmp)
                p.keyCipheredData = tmp
            elif value == 2:
                #  KeyAgreement.STATIC_UNIFIED_MODEL
                len_ = _GXCommon.getObjectCount(data)
                if len_ != 0:
                    raise ValueError("Invalid key parameters")
            else:
                raise ValueError("key-parameters")
        len_ = _GXCommon.getObjectCount(data)
        p.cipheredContent = data.remaining()
        sc = data.getUInt8()
        security = sc & 0x30
        ss = sc & 0x3
        if ss != SecuritySuite.AES_GCM_128:
            raise ValueError("Decrypt failed. Invalid security suite.")
        p.security = security
        invocationCounter = data.getUInt32()
        p.invocationCounter = invocationCounter
        tag = bytearray(12)
        encryptedData = None
        if security == Security.AUTHENTICATION:
            len_ = len(data) - data.position - 12
            encryptedData = bytearray(len_)
            data.get(encryptedData)
            data.get(tag)
            #  Check tag.
            cls.encryptAesGcm(p, encryptedData)
            if not GXDLMSChipperingStream.tagsEquals(tag, p.countTag):
                if transactionId != 0:
                    p.setInvocationCounter(transactionId)
                if not p.xml:
                    raise ValueError("Decrypt failed. Invalid tag.")
                p.xml.appendComment("Decrypt failed. Invalid tag.")
            return encryptedData
        ciphertext = None
        if security == Security.ENCRYPTION:
            len_ = len(data) - data.position
            ciphertext = bytearray(len_)
            data.get(ciphertext)
        elif security == Security.AUTHENTICATION_ENCRYPTION:
            len_ = len(data) - data.position - 12
            ciphertext = bytearray(len_)
            data.get(ciphertext)
            data.get(tag)
        aad = cls.getAuthenticatedData(p, ciphertext)
        iv = cls.getNonse(invocationCounter, p.systemTitle)
        gcm = GXDLMSChipperingStream(security, True, p.blockCipherKey, aad, iv, tag)
        gcm.write(ciphertext)
        if transactionId != 0:
            p.setInvocationCounter(transactionId)
        return gcm.flushFinalBlock()

security = Security.AUTHENTICATION_ENCRYPTION
blockCipherKey = (b'bbbbbbbbbbbbbbbb')
aad = (b'0bbbbbbbbbbbbbbbb')
iv = (b'qwertyui\x00\x00\x01\x9a')
# gcm = GXDLMSChipperingStream(security, True, blockCipherKey, aad, iv, None)
# print(gcm.tag)

# cls = 'gurux_dlms.GXDLMSChippering.GXDLMSChippering'
p = "gurux_dlms.AesGcmParameter.AesGcmParameter" 
def encrypt(data,aad,iv,ciphertext):
    tmp = GXDLMSChippering.encryptAesGcm(data,aad,iv,ciphertext)
    return tmp

# /////////////////////////////////////////////////////////////////////////////////////////////

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


authkey = "62626262626262626262626262626262" 
client_title = "7177657274797569"
# client_title =  "4350533030303033" #server title
llskey = "3132333435363738"
# llskey = "77777777777777777777777777777777"

def encrypt_aes_gcm(key, iv, additional_data, plaintext):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Provide additional data
    encryptor.authenticate_additional_data(additional_data)

    # Encrypt the plaintext
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Get the authentication tag
    tag = encryptor.tag

    return ciphertext, tag



def setup():
    # Example usage
    # //////////////////////////////////////////////////////////////////////////////
# 00 01 00 30 00 01 00 5F 60 5D A1 09 06 07 60 85 74 05 08 01 03 A6 0A 04 08 71 77 65 72 74 79 75 69 8A 02 07 80 8B 07 60 85 74 05 08 02 02 AC 12 80 10 6B 0E 27 64 4E 77 20 5B 1F 4B 08 55 11 0C 29 52 BE 23 04 21 21 1F 30 00 00 01 3F 
# EA C9 AB 86 88 40 6F EB F9 B3 70 AB CC 8D 
# D9 A0 26 FB 14 67 ED EA 28 18 C4 57
# ea c9 ab 86 88 40 6f eb f9 b3 70 ab cc 8d
    wrapper = "00010020000100"
    # length1 = 
    tag1 = "C8"
    # length = 
    security = "20"
    invocation = "0000019f"
    data = "2655d182142c40f78a099b713245cc80c1b4f73eb855fa04c060d1c17dd5af5ca07f5cab"
    
    # 01000000065f1f0400001e5dffff
    length1 = int((len(tag1)+len(security)+len(invocation)+len(data)+2)/2)
    print(length1)
    length = length1-2
    length1 = hex(length1)
    length1 = length1[2:]

    length = hex(length)

    length = length[2:]



# authkey = "4E53495F476C6F62616C6B65795F4541" 
# client_title = "4E53493030303030"
# llskey = "4E53495F53454331"
# /////////////////////////////////////////////////////////////////////////////

    # key = b'\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x41\x42\x43\x44\x45\x46'
    key = authkey
    # "62626262626262626262626262626262"
    key = bytes.fromhex(key)
    

    # iv = b'\x5A\x45\x4E\x30\x35\x30\x38\x30\x00\x00\x03\x0C'
    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    # additional_data = b'\x5A\x45\x4E\x30\x35\x30\x38\x30'
    additional_data = "01000000065f1f0400621e5dffff"
    additional_data = bytes.fromhex(additional_data)
    # 00010020000100496047A109060760857405080103A60A040871776572747975698A0207808B0760857405080201AC088006313233343536BE1704152113200000000092E1A1A26EFF582F0D13D540C77B
# 00010020000100496047A109060760857405080103A60A040871776572747975698A0207808B0760857405080201AC088006313233343536BE1704152113200000000092E1A1A26EFF582F0D13D540C77B
    # plaintext = b'\x9C\x10\x91\x09\x09\x3B\xA7\xB7\x53\x6D\x80\x6B\x60\xEB\x69\xC3\xBA\xED\x7C\x4E\x36\xF0\x30\x92\x33\x9F'
    plaintext = data
        # plaintext = "78C8069D5A2B607D0761927B7C"

    plaintext = bytes.fromhex(plaintext)

# 00 01 00 20 00 01 00 49 60 47 A1 09 06 07 60 85 74 05 08 01 03 A6 0A 04 08 71 77 65 72 74 79 75 69 8A 02 07 80 8B 07 60 85 74 05 08 02 01 AC 08 80 06 31 32 33 34 35 36 BE 17 04 15 21 13 20 00 00 00 01 34 69 6E 7E 1F 93 97 5A 7D 3C C2 17 45 D1

    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)
    # tag = "77777777777777777777777777777777"
    # tag = bytes.fromhex(tag)

    # decrypted_text = decrypt_aes_gcm(key, iv, additional_data, plaintext, tag)

    # print(f"Plaintext: {plaintext}")
    # print(f"Decrypted text: {decrypted_text}")
    print("Encrypted Data (hex):", ciphertext.hex())

    # print(frame)
    print("Auth Tag (hex):", tag.hex())
    return ciphertext.hex()

# ////////////////////////////////////////////////////////////////////////////////////////////////

# data = bytes.fromhex("c301c1000f0000280000ff01010910d213861210b14b523c82d2ed2dc7cf73")
data = bytes.fromhex("01000000065f1f0400401e5dffff")
iv = bytes.fromhex("7177657274797569000001ad")
# data = b'c301c1000f0000280000ff01010910d213861210b14b523c82d2ed2dc7cf73'

ciphertext = setup()

# gettag = encrypt(data,(b'0bbbbbbbbbbbbbbbb'),iv,ciphertext)


    # (b'\xc3\x01\xc1\x00\x0f\x00\x00(\x00\x00\xff\x01\x01\t\x10\xd2\x13\x86\x12\x10\xb1KR<\x82\xd2\xed-\xc7\xcfs'))


    # c301c1000f0000280000ff01010910d213861210b14b523c82d2ed2dc7cf73





    #//////////////////////////////////////////////////////////////////////////////////////////////////////////// 


import datetime
from random import randint
from time import sleep
import socket
import sys
import time
import calendar
import binascii
import datetime
# import mysql.connector
import codecs

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from datetime import datetime
from datetime import date
# from datetime import datetime
import datetime
from datetime import datetime

ip=[
# "192.168.1.100",
# "2401:4900:402C:F593::0002",
# "2401:4900:402C:F591::0002",
# "172.104.244.42",
"2401:4900:402C:F591::0002",
"2401:4900:84bd:6e9d::2",
# # # # 
"2401:4900:84bd:7027::2",
# # "2401:4900:402C:F58F::0002",#//zen
"2401:4900:84bd:6e21::2",
# "192.168.29.191",
# "192.168.29.191",

# "192.168.29.191",

# "192.168.29.191",

"2401:4900:84bd:6ffb::2",
"2401:4900:84bd:7027::2"
# "2401:4900:402C:F591::2",
# # "2401:4900:402c:f58f::2",
# "2401:4900:402c:f594::2"
# "2401:4900:402c:f593::2"
# "2401:4900:402c:f58e::2"
]

ip1=""
frame = ""
frame2 = ""


countip = 0
systitle = ""

# ////   CPS ///////

authkey = "62626262626262626262626262626262" 
client_title = "7177657274797569"
llskey = "3132333435363738"
# llskey = "77777777777777777777777777777777"

# ////////////inish////////

# authkey = "4E53495F476C6F62616C6B65795F4541" 
# client_title = "4E53493030303030"
# llskey = "4E53495F53454331"


# ////////////////////inish////////////////////

# authkey = "4E53495F476C6F62616C6B65795F4541" 
# client_title = "4E53493030303030"
# # llskey = "313233343536"
# llskey = "4E53495F53454331"

obis = [

"c001c1000701005e5b00ff0200", #instant
"c001c1000701005e5b00ff0300", #instant obis

"c001c1000701005e5b03ff0200", #instant scalar
"c001c1000701005e5b03ff0300", #instant scalar obis

"c001c100070100620100ff0200", #billing
"c001c100070100620100ff0300", #billing obis

"c001c1000701005e5b06ff0200", #billing scalar
"c001c1000701005e5b06ff0300", #billing scalar obis

    
]

profiles = ["INSTANTANEOUS PROFILE","INSTANTANEOUS PROFILE DATA OBIS","INSTANTANEOUS SCALAR ","INSTANTANEOUS SCALAR OBIS","BILLING PROFILE","BILLING PROFILE DATA OBIS","BILLING SCALAR","BILLING SCALAR OBIS"]
# ////////////////////////////////////////////////////////////////////////////////////////////////////


def encrypt_aes_gcm(key, iv, additional_data, plaintext):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Provide additional data
    encryptor.authenticate_additional_data(additional_data)

    # Encrypt the plaintext
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Get the authentication tag
    tag = encryptor.tag

    return ciphertext, tag
# def getCapacity(self):
#     if not self._data:
#         return 0
#     return len(self._data)

# def setUInt8(self, item, index=None):
#     if index is None:
#         self.setUInt8(item, self.size)
#         self.size += 1
#     else:
#         if index >= self.capacity:
#             self.capacity = index + self.__ARRAY_CAPACITY
#         self._data[index] = item

#
#      Push the given byte into this buffer at the current position, and
#      then
#      increments the position.
#
#      @param item
#                 The byte to be added.
#

def instaframing(iv):

    # iv = 3
    wrapper = "00010020000100"
    # length1 = 
    aarq_tag = "60"
    # length = 
    application_context_name = "A109060760857405080103"
    extra_bytes = "A60A0408"
    sys_title = client_title
    aARQ_aCSE_rEQs = "8A020780"
    auth_mechanism_name = "8B0760857405080201"

    # print(lenpwd)



    # print(pwd_tag)
    # data.setUInt8(llskey)

    auth_tag_length = "BE1704152113"
    security = "20"
    iv = format(iv, '#08x')
    iv = iv[2:]
    invocation = "00"+iv
    # print(invocation)
    llskey1 = returnencryt(llskey,invocation)
    pwd = llskey
    # print(lenpwd1)
    llslen = int(len(llskey)/2)
    formatted_hex_value = format(llslen, '#04x')
    lenpwd = formatted_hex_value[2:]
    llslen1 = llslen + 2
    formatted_hex_value = format(llslen1, '#04x')
    lenpwd1 = formatted_hex_value[2:]
    pwd_tag = "AC"+lenpwd1+"80"+lenpwd
    data = "01000000065F1F0400001E1DFFFF"
    # authkey1 = b"62626262626262626262626262626262" 
    # nonce  = bytes.fromhex(sys_title+invocation)
    # data1 = b"01000000065f1f0400001e5dffff"
    # ciphertext1, tag = encrypt_with_aes_gcm(data1, authkey1,nonce)

    # tag1 = "43c6ab92c8b528a80c25d5f0"
 
    # data = "0101102c566f651b24365f037e2b6a5e572e230000065f1f040000181dffffb218e7dbe989b48e28174740"

    # b218e7dbe989b48e28174740
    length1 = int((len(aarq_tag)+len(application_context_name)+len(extra_bytes)+len(sys_title)+len(aARQ_aCSE_rEQs)+len(auth_mechanism_name)+len(pwd_tag)+len(pwd)+len(auth_tag_length)+len(security)+len(invocation)+len(data)+2)/2)
    # print(length1)
    length = length1-2
    length1 = hex(length1)
    length1 = length1[2:]

    length = hex(length)

    length = length[2:]

# ------------------------------------------------------------------------------------------------------------------------------------------
    
    key = authkey #//cps
    # key = "303132333435363738394142434445460A"
    key = bytes.fromhex(key)
    

    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    additional_data = client_title #//systemtitle cps
    # additional_data = "68656C6C6F" #//systemtitle zen

    additional_data = bytes.fromhex(additional_data)

    plaintext = data

    plaintext = bytes.fromhex(plaintext)

    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)

    # print("Encrypted Data (hex):", ciphertext.hex())
    data = bytes.fromhex(data)
    # gettag = encrypt(data,(b'0bbbbbbbbbbbbbbbb'),iv,ciphertext.hex())

    frame = wrapper+str(length1)+aarq_tag+str(length)+application_context_name+extra_bytes+sys_title+aARQ_aCSE_rEQs+auth_mechanism_name+pwd_tag+pwd+auth_tag_length+security+invocation+str(ciphertext.hex())
    
    # print(frame)
    return frame

def returnencryt(data,invocation):

    # print(profilename)
    # wrapper = "00010020000100"
    # # length1 = 
    # tag1 = "C8"
    # # length = A6422F92CEEB1769367EFD3C
    # security = "20"
    # iv = format(iv, '#08x')
    # iv = iv[2:]
    # invocation = "00"+iv
    # # print(invocation)
    # # data = "c001c100070100620100ff0200"
    # length1 = int((len(tag1)+len(security)+len(invocation)+len(data)+2)/2)
    # # print(length1)
    # length = length1-2
    # length1 = hex(length1)
    # length1 = length1[2:]

    # length = hex(length)

    # length = length[2:]

# -----------------------------------------------------------------------------------------------
    
    key = authkey #//cps
    # key = "303132333435363738394142434445460A"
    key = bytes.fromhex(key)
    

    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    additional_data = client_title #//systemtitle cps
    # additional_data = "68656C6C6F" #//systemtitle zen

    additional_data = bytes.fromhex(additional_data)

    plaintext = data

    plaintext = bytes.fromhex(plaintext)



    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)

    # print("Encrypted Data (hex):", ciphertext.hex())

    # print(frame)
    return ciphertext.hex()
    # print("Auth Tag (hex):", tag.hex())


def COMMAND_FRAMER(data,iv,profilename):

    print(profilename)
    wrapper = "00010020000100"
    # length1 = 
    tag1 = "C8"
    # length = 
    security = "20"
    # iv = format(iv, '#08x')
    # iv = iv[2:]
    invocation = iv
    # print(invocation)
    # data = "c001c100070100620100ff0200"
    length1 = int((len(tag1)+len(security)+len(invocation)+len(data)+2)/2)
    # print(length1)
    length = length1-2
    length1 = hex(length1)
    length1 = length1[2:]

    length = hex(length)

    length = length[2:]

# -----------------------------------------------------------------------------------------------
    
    key = authkey #//cps
    # key = "303132333435363738394142434445460A"
    key = bytes.fromhex(key)
    

    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    additional_data = client_title #//systemtitle cps
    # additional_data = "68656C6C6F" #//systemtitle zen

    additional_data = bytes.fromhex(additional_data)

    plaintext = data

    plaintext = bytes.fromhex(plaintext)



    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)

    # print("Encrypted Data (hex):", ciphertext.hex())

    frame = wrapper+str(length1)+tag1+str(length)+security+invocation+str(ciphertext.hex())
    # print(frame)
    return frame
    # print("Auth Tag (hex):", tag.hex())

# -------------------------------------------------------------------------------------------

def COMMAND_FRAMER_LOAD(iv,profilename,from_date,todate):

    print(profilename)
    wrapper = "00010020000100"
    # length1 = 
    tag1 = "C8"
    # length = 
    security = "20"
    iv = format(iv, '#08x')
    iv = iv[2:]
    invocation = "00"+iv
    # print(invocation)
    data1 = "c001c100070100630100ff0201010204020412000809060000010000ff0f02120000090c"
    a = "00000000014a00"
    middle_tag = "090c"
    end="0100"
    length1 = int((len(tag1)+len(security)+len(invocation)+len(data1)+len(from_date)+len(a)+len(middle_tag)+len(todate)+len(a)+len(end)+2)/2)
    # print(length1)
    length = length1-2
    length1 = hex(length1)
    length1 = length1[2:]

    length = hex(length)

    length = length[2:]
    data = data1+from_date+a+middle_tag+todate+a+end
    print(data)
# -----------------------------------------------------------------------------------------------
    
    key = authkey #//cps
    # key = "303132333435363738394142434445460A"
    key = bytes.fromhex(key)
    

    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    additional_data = client_title #//systemtitle cps
    # additional_data = "68656C6C6F" #//systemtitle zen

    additional_data = bytes.fromhex(additional_data)

    plaintext = data

    plaintext = bytes.fromhex(plaintext)



    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)

    print("Encrypted Data (hex):", ciphertext.hex())

    frame = wrapper+str(length1)+tag1+str(length)+security+invocation+str(ciphertext.hex())
    # print(frame)
    return frame
    # print("Auth Tag (hex):", tag.hex())


# -------------------------------------------------------------------------------------------

def setup1(iv,count):


    wrapper = "00010020000100"
    # length1 = 
    tag1 = "C8"
    # length = 
    security = "20"
    count = format(count, '#08x')
    count = count[2:]
    invocation = iv
    print(invocation)    
    data = "c002c100"+count
    length1 = int((len(tag1)+len(security)+len(invocation)+len(data)+2)/2)
    # print(length1)
    length = length1-2
    length1 = hex(length1)
    length1 = length1[2:]

    length = hex(length)

    length = length[2:]

    length1 = "0"+str(length1)
    length = "0"+str(length)


# /////////////////////////////////////////////////////////////////////////////


    key = authkey#//cps
    key = bytes.fromhex(key)
    

    iv = client_title+invocation
    iv = bytes.fromhex(iv)
    

    # additional_data = b'\x5A\x45\x4E\x30\x35\x30\x38\x30'
    additional_data = client_title #//systemtitle cps

    additional_data = bytes.fromhex(additional_data)
    plaintext = data

    plaintext = bytes.fromhex(plaintext)

    ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)

    # print("RES1 = ", ciphertext.hex())

    frame = wrapper+str(length1)+tag1+str(length)+security+invocation+str(ciphertext.hex())
    # print(frame)
    return frame
    # print("Auth Tag (hex):", tag.hex())




# ----------------------------------TCP PART----------------------------------------#

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_with_aes_gcm(data, key,nonce):
    """
    Encrypts data using AES-GCM and returns the encrypted data (ciphertext),
    the nonce, and the authentication tag.
    
    Parameters:
    - data: The plaintext data to be encrypted (bytes).
    - key: The encryption key (bytes).
    
    Returns:
    - ciphertext: The encrypted data (bytes).
    - nonce: The nonce used during encryption (bytes).
    - tag: The authentication tag (bytes).
    """
    # Generate a random 96-bit (12 bytes) nonce
    # nonce = b"717765727479756900000131"
    
    # Create an AESGCM object with the given key
    aesgcm = AESGCM(key)
    
    # Encrypt the data
    # The encrypt method returns the ciphertext concatenated with the authentication tag
    ct = aesgcm.encrypt(nonce, data, None)  # Associated data (None) could be included if needed
    
    # In AESGCM.encrypt, the tag is appended to the ciphertext.
    # The tag length for AES-GCM is typically 16 bytes (128 bits).
    ciphertext, tag = ct[:-16], ct[-16:]
    
    return ciphertext, nonce, tag

# Example usage
# key = b"62626262626262626262626262626262"
# data = b"01000000065f1f0400621e5dffff"  # Data to encrypt
# ciphertext, nonce, tag = encrypt_with_aes_gcm(data, key)

# print("Ciphertext:", ciphertext.hex())
# print("Nonce:", nonce)
# print("Tag:", tag.hex())

def netcat(hostname = str(ip1), port = 4001,data =frame):
# def netcat(hostname = '117.230.240.33', port = 4001, content = "127EA0190321326FD8E6E600C0018100010000600100FF02008C6D7E12"):
    print(str(hostname))
    now = datetime.now()
    print(str(port))



    # file.write(str(now)+" : ip "+str(hostname)+"\n")

    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) #change
    # s.settimeout(10)
    s.connect((str(hostname), port))
    # time.sleep(10)
    now = datetime.now()
    # print(now)
    count = 0
    flag=0

    obiscount = 0
    insta = 0
    load = 0
    profilecount = 0
    extracount = 0
    while 1:
        if(count == 0):
            print("AARQ")

            commandforprofile = "000100100001001F601DA109060760857405080101BE10040E01000000065F1F0400001E5DFFFF"
        else:
            if(count == 1):
                commandforprofile = "000100100001000DC001C1000100002B0102FF0200"
                
                # commandforprofile = "0001003000010032CB303000000001EE9EAE50B602250051D3289FD7DC2FCFB3F9234CCC58B010BF1EB77241A521A483B9A025081B48DB0FBDD1"
            else:
                if(count == 2):    
                # commandforprofile = COMMAND_FRAMER_LOAD(0,"LOAD PROFILE","07e8021c03","07e8021d04")
                # load = 0
                    commandforprofile = "00010010000100056203800100"
                else:
                    if(count == 3): 
                        commandforprofile = instaframing(systitle+1)
    
                    else:
                        # if(count == 4):
                        # systitle = 
                        iv = format(systitle +2+obiscount+extracount, '#08x')
                        iv = iv[2:]
                        invocation = "00"+iv
                        print(invocation)    
                        #     data = bytes.fromhex("c301c1000f0000280000ff01010910d213861210b14b523c82d2ed2dc7cf73")
                        #     data1 = returnencryt("c301c1000f0000280000ff01010910d213861210b14b523c82d2ed2dc7cf73",invocation)
                        #     data2 = bytes.fromhex(data1)
                        #     print(systitle1)
                        #     nonce = bytes.fromhex(client_title+str(invocation))
                        #     gettag = encrypt(data,(b'0bbbbbbbbbbbbbbbb'),nonce,data1)

                        #     commandforprofile = "0001003000010032CB3030"+invocation+data1+gettag
                        #     # iv = iv+1
                        #     # commandforprofile = COMMAND_FRAMER(obis[obiscount],obiscount,profiles[profilecount])
                        insta = 1
                        commandforprofile = COMMAND_FRAMER(obis[obiscount],invocation,profiles[profilecount])
    
                        # else:
                        #     if(count == 5): 
                        #         iv = format(systitle+3, '#08x')
                        #         iv = iv[2:]
                        #         invocation = "00"+iv
                        #         print(invocation)   
                        #         data1 = returnencryt("c301c10046000060030aff01010f00",invocation) 
                        #         data = bytes.fromhex("c301c10046000060030aff01010f00") 
                        #         nonce = bytes.fromhex(client_title+str(invocation))
                        #         data2 = bytes.fromhex(data1)

                        #         gettag = encrypt(data,(b'0bbbbbbbbbbbbbbbb'),nonce,data2)
                          
                        #         commandforprofile = "0001003000010022CB2030"+invocation+data1+gettag
                        #         # iv = iv+1
                        #     else:
                                 
                        #         iv = format(systitle+4, '#08x')
                        #         iv = iv[2:]
                        #         invocation = "00"+iv
                        #         print(invocation) 
                        #         data1 = returnencryt("c301c10046000060030aff02010f00",invocation)     
                        #         data = bytes.fromhex("c301c10046000060030aff02010f00") 
                        #         nonce = bytes.fromhex(client_title+str(invocation))
                        #         data2 = bytes.fromhex(data1)

                        #         gettag = encrypt(data,(b'0bbbbbbbbbbbbbbbb'),nonce,data2)

                        #         commandforprofile = "0001003000010022CB2030"+invocation+data1+gettag
                                # iv = iv+1

                # commandforprofile = COMMAND_FRAMER(obis[obiscount],obiscount+2,profiles[profilecount])
        # instantobis = COMMAND_FRAMER(obis[obiscount],"00000000","INSTANTANEOUS PROFILE DATA OBIS")

        # instantscalar = COMMAND_FRAMER(obis[obiscount],"00000000","INSTANTANEOUS SCALAR ")
        # instantscalarobis = COMMAND_FRAMER(obis[obiscount],"00000000","INSTANTANEOUS SCALAR OBIS")

        # billing = COMMAND_FRAMER(obis[obiscount],"00000000","BILLING PROFILE")
        # billingobis = COMMAND_FRAMER(obis[5],"00000000","BILLING PROFILE DATA OBIS")

        # billingscalar = COMMAND_FRAMER(obis[6],"00000000","BILLING SCALAR")
        # billingscalarobis = COMMAND_FRAMER(obis[7],"00000000","INSTANTANEOUS SCALAR OBIS")

    #     commands=[
    # # "7EA0070341935A647E",
    #     # "00010020000100496047A109060760857405080103A60A040871776572747975698A0207808B0760857405080201AC088006313233343536BE1704152113200000000134696E7E1F93975A7D3CC21745D1",
    #     #cps
    #     data,
    #     instant,instantobis,instantscalar,instantscalarobis,billing,billingobis,billingscalar,billingscalarobis,
    #     # "00010020000100546052A109060760857405080103A60A04085A454E31323334358A0207808B0760857405080201AC07800568656C6C6FBE230421211F3000000F209F5BD18A510F7852E5C1F94A3DFA7D0F042481671D69EB18214E",#//#zen
    #     "000100100001001f601da109060760857405080101be10040e01000000065f1f0400001e1dffff",

    #     # "7EA02B032110FBAFE6E600601DA109060760857405080101BE10040E01000000065F1F0400001E5DFFFFB3E27E"
    #     # "7EA044034110B3E1E6E600603680020284A1090607608574050801018A0207808B0760857405080201AC0680046C6E7431BE10040E01000000065F1F0400001E1DFFFF85157E",
    #     # "7EA0190341323ABDE6E600C001C1000701005E5B00FF020091427E",
    #     # "7EA00703415144817E",
    #     # "7EA00703417146A07E",
    #     # "7EA00703419148477E",
    #     # "7EA00703415356A27E"
    #     ]        
               
            
        # print(count)
        con1 = bytearray.fromhex(commandforprofile)
        # output = content.decode()
        s.sendall(con1)
        con1 = binascii.hexlify(con1)
        output = str((con1), 'UTF-8')
        print ('REQUEST = ' + str(output)+"\n")
        data1 = s.recv(1024)
        # now = datetime.now()
        # print(now)

        # print ("RES = " +str(data1)+"\n")

        con2 = binascii.hexlify(data1)
        output1 = str((con2), 'UTF-8')
        print ("RES = " +str(output1)+"\n")
        # print(insta)
        if(count == 1):
            res = responseparsing(output1,2,0,0)
            # count1=count1+1
            if(res == "1"):
                return;
        else:
            if(count == 3):

                res = responseparsing(output1,1,0,0)

        # count = count +1    
            else:
                if(insta == 1):
                    res = responseparsing(output1,3,0,systitle +2+obiscount+extracount)
                        
                    count1 = 0
                    if(res == "1"):
                        return;
                    if(load == 1):    
                        while 1:    
                            if(len(res) > 10):
                                con1 = bytearray.fromhex(res)
                                # print(con1)
                                s.sendall(con1)
                                con1 = binascii.hexlify(con1)

                                output = str((con1), 'UTF-8')
                                print ('REQUEST = ' + str(output)+"\n")
                                data1 = s.recv(1024)
                                con2 = binascii.hexlify(data1)
                                output1 = str((con2), 'UTF-8')
                                print ("RES = " +str(output1)+"\n")
                                res = responseparsing(output1,2,count1,0)
                                count1=count1+1
                                if(res == "1"):
                                    return;
                    else:
                        if(len(res) > 10):
                            con1 = bytearray.fromhex(res)
                            # print(con1)
                            s.sendall(con1)
                            con1 = binascii.hexlify(con1)

                            output = str((con1), 'UTF-8')
                            print ('REQUEST = ' + str(output)+"\n")
                            data1 = s.recv(1024)
                            con2 = binascii.hexlify(data1)
                            output1 = str((con2), 'UTF-8')
                            print ("RES111 = " +str(output1)+"\n")
                            extracount = extracount+1

                            res = responseparsing(output1,3,count1,systitle +2+obiscount+extracount)
                            if(len(res) > 10):
                                con1 = bytearray.fromhex(res)
                                # print(con1)
                                s.sendall(con1)
                                con1 = binascii.hexlify(con1)

                                output = str((con1), 'UTF-8')
                                print ('REQUEST = ' + str(output)+"\n")
                                data1 = s.recv(1024)
                                con2 = binascii.hexlify(data1)
                                output1 = str((con2), 'UTF-8')
                                print ("RES111 = " +str(output1)+"\n")
                                
                                res = responseparsing(output1,3,count1,1)
                                extracount = extracount+1
                                count1=count1+1
                                if(res == "1"):
                
                                    return;            
                
        if(count > 3):        
            obiscount = obiscount+1
            profilecount = profilecount+1
        else:    
            count=count+1
        # count = count +1
    
        # if(count > 1):
            # while 1:
            #     # time.sleep(2)
            #     data1 = s.recv(1024)
            #     # print ("RES = " +str(data1)+"\n") 
            #     con2 = binascii.hexlify(data1)
            #     output1 = str((con2), 'UTF-8')
            #     print ("RES = " +str(output1)+"\n")
        # if(len(output1)>1):
        #     data=(output1[2])+(output1[3])
        # if(count == 2):
        #     flag = 1
        # if(flag == 1):
        #     if(data == "a8"):
        #        count = count+1
        #     else:
        #        flag = 0 
        #        count = 6 
        # else:        
        #     count=count+1
        # # print ("--------------------------------------------------------------------------------------------------"+"\n")

        # file.write(str(now)+" : "+output1+"\n")
        # print(len(obis))
        if(obiscount > len(obis)-1):
        #     # file.write("--------------------------------------------------------------------------------------------------"+"\n")
        #     # file.close()
            break

    s.close()





def encrypt_aes_gcm(key, iv, additional_data, plaintext):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Provide additional data
    encryptor.authenticate_additional_data(additional_data)

    # Encrypt the plaintext
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Get the authentication tag
    tag = encryptor.tag

    return ciphertext, tag

def update_title(systemtitle1):
    global systitle
    # systemtit = bytes.fromhex(systemtitle1).decode('utf-8')

    print(systemtitle1)  # Accessing the global variable
    systitle = systemtitle1

def update_title1(systemtitle1):
    global systitle1
    # systemtit = bytes.fromhex(systemtitle1).decode('utf-8')

    print(systemtitle1)  # Accessing the global variable
    systitle1 = systemtitle1    

def responseparsing(response,flag,iv1,b):

    if(flag == 3):

        response1 = response[12:len(response)]
        # print(response1)
        lengthofres = response1[0:4]
        # print(lengthofres)
        tagofre = response1[6:8]
        # print(tagofre)
        index = response1.index(tagofre) 
        if(tagofre == "81"):

        # index = response1.index("2000")
        # print(index) 
            invocation = response1[index+6:index+14]
            # print(invocation)
            data = response1[index+14:len(response1)]
            # print(data)
        else:
            if(tagofre == "82"):
                invocation = response1[index+6+2:index+14+2]
                # print(invocation)
                data = response1[index+14+2:len(response1)]
                # print(data)

            else:
                invocation = response1[index+4:index+8+4]
                # print(invocation)
                data = response1[index+8+4:len(response1)]
                # print(data)


    else: 
        if(flag == 1):
            if(len(response)>512):
                 return "1"
            response1 = response[72:len(response)]
            print(response)
            type1 = response1[0:2]
            # print(type1)
            invocation = "00000000"
            # print(invocation)
            systemtitle1 = response1[2:2+int(type1)*2]
            print(systemtitle1)

            systemtitle2 = bytes.fromhex(systemtitle1).decode('utf-8')
            print(systemtitle2)

            update_title1(systemtitle1)

        else: 
            if(flag == 2):
                if(len(response)>512):
                     return "1"
                response1 = response[26:len(response)]
                print(response1)
                # type1 = response1[0:2]
                # print(type1)
                invocation = int(response1,16)
                # print(invocation)
                # systemtitle1 = response1[2:2+int(type1)*2]
                print(invocation)

                # systemtitle1 = bytes.fromhex(systemtitle1).decode('utf-8')
                update_title(invocation)        
    # print(systitle)

# /////////////////////////////////////////////////////////////////////////////
    if(flag == 3):
        key = authkey
        key = bytes.fromhex(key)
        
        iv = systitle1+invocation
        iv = bytes.fromhex(iv)
        
        additional_data = systitle1
        additional_data = bytes.fromhex(additional_data)
        plaintext = data

        plaintext = bytes.fromhex(plaintext)


        ciphertext, tag = encrypt_aes_gcm(key, iv, additional_data, plaintext)
        print("Encryted RES = ", ciphertext.hex())
        res = ciphertext.hex()[0:8]

        if(res == "c402c100"):
            # systitle = systitle +3
            # print(b)
            count = 1
            if(b == 1):
               count = 2
            iv = format(b+1, '#08x')
            iv = iv[2:]
            invocation = "00"+iv
            print(invocation)

            R = setup1(invocation,count)
            print("-----------------------------------------------------------------------------------------------------------------")

            return R
    print("-----------------------------------------------------------------------------------------------------------------")
        
    return ""        

# while 1:
    # print(len(ip))
data = "instaframing()"
netcat(ip[countip],4001,data)
print("END")

    