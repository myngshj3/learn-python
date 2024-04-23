
use strict;
use warnings;

# check argument
my $java = shift@ARGV;
unless (defined$java) {
    print STDERR "argument not specified";
    exit 1;
}

# extract multibyte symbols
my $status = system("perl extract_functions.pl $java | uniq > $java.replace-rule");
unless ($status == 0) {
    print STDERR "$java: AST generation failed. exit status: $status\n";
    exit $status;
}

# replace multibyte symbols
$status = system("python replace.py forward $java.replace-rule $java");
unless ($status == 0) {
    print STDERR "$java: forward-replacement failed. exit status: $status\n";
    exit $status;
}

# generate AST
$status = system("pmd ast-dump --language=java --format=xml --file=$java > $java.xml");
unless ($status == 0) {
    print STDERR "$java: AST generation failed. exit status: $status\n";
    exit $status;
}

# convert AST to JSON
$status = system("python xml2dict.py $java.xml > $java.json");
unless ($status == 0) {
    print STDERR "$java: AST generation failed. exit status: $status\n";
    exit $status;
}

# replace multibyte symbols
$status = system("python replace.py backward $java.replace-rule $java");
unless ($status == 0) {
    print STDERR "$java: backward-replacement failed. exit status: $status\n";
    exit $status;
}

