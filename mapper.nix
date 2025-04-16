{ buildPythonApplication, setuptools, dateutil, beautifulsoup4, mailmanPackages, lxml }:

buildPythonApplication {
  pname = "mailman-archive-mapper";
  version = "0.1";
  format = "pyproject";
  src = ./.;
  build-system = [ setuptools ];
  propagatedBuildInputs = [
    beautifulsoup4
    mailmanPackages.hyperkitty
    dateutil
    lxml
  ];
}
