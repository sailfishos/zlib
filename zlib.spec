%define keepstatic 1

Name:       zlib
Summary:    The zlib compression and decompression library
Version:    1.2.5
Release:    1
Group:      System/Libraries
License:    zlib and Boost
URL:        http://www.gzip.org/zlib/
Source0:    http://www.zlib.net/zlib-%{version}.tar.gz
Patch0:     zlib-1.2.4-autotools.patch
Patch1:     zlib-1.2.5-lfs-decls-bmc-11751.patch
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
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description static
The zlib-static package includes static libraries needed
to develop programs that use the zlib compression and
decompression library.


%package -n minizip
Summary:    Minizip manipulates files from a .zip archive
Group:      System/Libraries
Requires:   %{name} = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description -n minizip
Minizip manipulates files from a .zip archive.

%package -n minizip-devel
Summary:    Development files for the minizip library
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description -n minizip-devel
This package contains the libraries and header files needed for
developing applications which use minizip.


%package devel
Summary:    Header files and libraries for Zlib development
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description devel
The zlib-devel package contains the header files and libraries needed
to develop programs that use the zlib compression and decompression
library.



%prep
%setup -q -n %{name}-%{version}

# zlib-1.2.4-autotools.patch
%patch0 -p1
# zlib-1.2.5-lfs-decls-bmc-11751.patch
%patch1 -p1
mkdir contrib/minizip/m4
cp minigzip.c contrib/minizip
iconv -f windows-1252 -t utf-8 <ChangeLog >ChangeLog.tmp
mv ChangeLog.tmp ChangeLog

%build
CFLAGS=$RPM_OPT_FLAGS ./configure --libdir=%{_libdir} --includedir=%{_includedir} --prefix=%{_prefix}

#ensure 64 offset versions are compiled (do not override CFLAGS blindly)
export CFLAGS="`egrep ^CFLAGS Makefile | sed -e 's/CFLAGS=//'`"
export SFLAGS="`egrep ^SFLAGS Makefile | sed -e 's/SFLAGS=//'`"

#
# first,build with -fprofile-generate to create the profile data
#
make %{?_smp_mflags} CFLAGS="$CFLAGS -pg -fprofile-generate" SFLAGS="$SFLAGS -pg -fprofile-generate"

#
# Then run some basic operations using the minigzip test program
# to collect the profile guided stats
# (in this case, we compress and decompress the content of /usr/bin)
#
cp Makefile Makefile.old
make test -f Makefile.old LDFLAGS="libz.a -lgcov"
cat /usr/bin/* | ./minigzip | ./minigzip -d &> /dev/null

#
# Now that we have the stats, we need to build again, using -fprofile-use
# Due to the libtool funnies, we need to hand copy the profile data to .libs
#
make clean
mkdir .libs
cp *gcda .libs

#
# Final build, with -fprofile-use
#
make %{?_smp_mflags} CFLAGS="$CFLAGS -fprofile-use"  SFLAGS="$SFLAGS -fprofile-use"  


cd contrib/minizip
%reconfigure
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
%make_install

mkdir $RPM_BUILD_ROOT/%{_lib}
mv $RPM_BUILD_ROOT%{_libdir}/libz.so.* $RPM_BUILD_ROOT/%{_lib}/

reldir=$(echo %{_libdir} | sed 's,/$,,;s,/[^/]\+,../,g')%{_lib}
oldlink=$(readlink $RPM_BUILD_ROOT%{_libdir}/libz.so)
ln -sf $reldir/$(basename $oldlink) $RPM_BUILD_ROOT%{_libdir}/libz.so

cd contrib/minizip
make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la


%check
make test


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%post -n minizip -p /sbin/ldconfig

%postun -n minizip -p /sbin/ldconfig




%files
%defattr(-,root,root,-)
/%{_lib}/libz.so.*


%files static
%defattr(-,root,root,-)
%doc README
%{_libdir}/libz.a

%files -n minizip
%defattr(-,root,root,-)
%doc contrib/minizip/MiniZip64_info.txt contrib/minizip/MiniZip64_Changes.txt
%{_libdir}/libminizip.so.*

%files -n minizip-devel
%defattr(-,root,root,-)
%dir %{_includedir}/minizip
%{_includedir}/minizip/*.h
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc

%files devel
%defattr(-,root,root,-)
%doc README doc/algorithm.txt example.c README ChangeLog FAQ
%{_libdir}/libz.so
%{_includedir}/zconf.h
%{_includedir}/zlib.h
%{_mandir}/man3/zlib.3*
%{_libdir}/pkgconfig/zlib.pc

