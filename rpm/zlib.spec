Name:       zlib

%define binutils_ver %(rpm -q --queryformat='%%{version}' binutils | awk -F. '{print $1$2}')
%define keepstatic 1

Summary:    The zlib compression and decompression library
Version:    1.3.1
Release:    1
License:    zlib and Boost
URL:        https://github.com/sailfishos/zlib
Source0:    %{name}-%{version}.tar.gz
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool

%description
Zlib is a general-purpose, patent-free, lossless data compression
library which is used by many different programs.


%package static
Summary:    Static libraries for Zlib development
Requires:   %{name} = %{version}-%{release}

%description static
The zlib-static package includes static libraries needed
to develop programs that use the zlib compression and
decompression library.


%package -n minizip
Summary:    Minizip manipulates files from a .zip archive
Requires:   %{name} = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description -n minizip
Minizip manipulates files from a .zip archive.

%package -n minizip-devel
Summary:    Development files for the minizip library
Requires:   %{name} = %{version}-%{release}

%description -n minizip-devel
This package contains the libraries and header files needed for
developing applications which use minizip.


%package devel
Summary:    Header files and libraries for Zlib development
Requires:   %{name} = %{version}-%{release}

%description devel
The zlib-devel package contains the header files and libraries needed
to develop programs that use the zlib compression and decompression
library.


%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
Man pages and other documentation for %{name} and minizip.


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC"
export LDFLAGS="$LDFLAGS -Wl,-z,relro -Wl,-z,now"
./configure --libdir=%{_libdir} --includedir=%{_includedir} --prefix=%{_prefix}

%make_build

pushd contrib/minizip
%reconfigure --enable-static=no
%make_build
popd

%install
%make_install

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} \
        README doc/algorithm.txt test/example.c ChangeLog FAQ \
        contrib/minizip/MiniZip64_info.txt \
        contrib/minizip/MiniZip64_Changes.txt

pushd contrib/minizip
%make_install
# https://github.com/madler/zlib/pull/229
rm $RPM_BUILD_ROOT%_includedir/minizip/crypt.h

find $RPM_BUILD_ROOT -name '*.la' -delete
popd

%check
make test

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post -n minizip -p /sbin/ldconfig

%postun -n minizip -p /sbin/ldconfig

%files
%license LICENSE
%{_libdir}/libz.so.*

%files static
%license LICENSE
%{_libdir}/libz.a

%files -n minizip
%license LICENSE
%{_libdir}/libminizip.so.*

%files -n minizip-devel
%dir %{_includedir}/minizip
%{_includedir}/minizip/*.h
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc

%files devel
%{_libdir}/libz.so
%{_includedir}/zconf.h
%{_includedir}/zlib.h
%{_libdir}/pkgconfig/zlib.pc

%files doc
%{_mandir}/man*/%{name}.*
%{_docdir}/%{name}-%{version}
