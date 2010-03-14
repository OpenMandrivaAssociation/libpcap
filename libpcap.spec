%define major 1
%define libname %mklibname pcap %major
%define develname %mklibname pcap -d

Summary:        A system-independent interface for user-level packet capture
Name:		libpcap
Version:	1.0.0
Release:	%mkrel 8
License:	BSD
Group:		System/Libraries
URL:		http://www.tcpdump.org/
Source0:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
Patch0:		libpcap-1.0.0-LDFLAGS.diff
# (misc) fix the -i any, 
# http://sourceforge.net/tracker/?func=detail&aid=2593897&group_id=53067&atid=469577
# commit 8fa17a5a554aaeb85d3ec4118b45a31f1efd6808 from upstream
Patch1:     libpcap-1.0.0-fix_handling_of_any.diff
# (misc) use usbmon to sniff on usb bus, and allow to use tcpdump -i usb0
# patch from debian, applied upstream ( 3866e831 )
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=520259
Patch2:     libpcap-1.0.0-fix_usb_network_sniffing.diff
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	bluez-devel
BuildRequires:	autoconf2.5
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{libname}
Summary:	A system-independent interface for user-level packet capture
Group:          System/Libraries
Obsoletes:      %{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
Provides:       pcap = %{version}-%{release}

%description -n	%{libname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{develname}
Summary:	Static library and header files for the pcap library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	pcap-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname pcap -d 0}

%description -n	%{develname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

This package contains the static pcap library and its header files needed to
compile applications such as tcpdump, etc.

%prep

%setup -q
%patch0 -p0
%patch1 -p1
%patch2 -p0

%build
%serverbuild

%configure2_5x \
    --enable-ipv6

%make "CCOPT=$CFLAGS -fPIC" all
%make "CCOPT=$CFLAGS -fPIC" shared

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_bindir}

make DESTDIR=%{buildroot} install
make DESTDIR=%{buildroot} install-shared

ln -snf libpcap.so.%{major} %{buildroot}%{_libdir}/libpcap.so

# install additional headers
install -m0644 pcap-int.h %{buildroot}%{_includedir}/
install -m0644 pcap/bluetooth.h %{buildroot}%{_includedir}/pcap/

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc README* CREDITS INSTALL.txt LICENSE
%{_libdir}/libpcap.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%doc CHANGES TODO
%{_bindir}/pcap-config
%dir %{_includedir}/pcap
%{_includedir}/pcap/*.h
%{_includedir}/*.h
%{_libdir}/libpcap.so
%{_libdir}/libpcap.a
%{_mandir}/man?/*
