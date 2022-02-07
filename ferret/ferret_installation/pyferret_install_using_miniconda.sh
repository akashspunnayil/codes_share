#!/bin/sh

CONDABASE=/usr/local/miniconda
wrapper=pyferret.sh
echo=/bin/echo # not necessary, because we don't use "\c" any longer.

#--- Check if pwd is writable.
if [ ! -w $(pwd) ]; then
    $echo "The present directory is not writable." >&2
    $echo "Please go to somwhere you have write permission" >&2
    $echo "  and run this script there again." >&2
    exit 1
fi

#--- Have homebrew ? --
type brew > /dev/null 2> /dev/null
if [ $? -ne 0 ]; then
    $echo "It seems you don't have Homebrew installed." >&2
    $echo "If you know you already have miniconda installed," >&2
    $echo "   modify this script to skip this check." >&2
    $echo "Otherwise, install Homebrew (https://brew.sh) and come back." >&2
    exit 2
fi

#--- Install miniconda ---
conda="$CONDABASE/bin/conda"
if [ -e "$conda" ]; then
    $echo "You seems to already have miniconda in $CONDABASE."
    read -p "Shall I use it? If unsure, say yes [y/n]: " ans
    case "$ans" in
    Y|y|YES|Yes|yes) ;;
    *)
	$echo "Okay, you seem to want to use another miniconda installation."
	$echo "Modify the CONDABASE variable in this script"
	$echo "   and come back again."
	exit 0;;
    esac
else
    $echo "You don't seem to have miniconda yet."
    read -p "Shall I install it? If unsure, say yes [y/n]: " ans
    case "$ans" in
    Y|y|YES|Yes|yes) ;;
    *)
	$echo "Okay, I suppose you have a miniconda installation"
	$echo "  somewhere I didn't expect."
	$echo "Modify the CONDABASE variable in this script"
	$echo "   and come back again."
	exit 0;;
    esac
    brew cask install miniconda
fi

#--- Install PyFerret ---
conda="$CONDABASE/bin/conda"
if [ ! -e "$conda" ]; then
    $echo "I expected to find miniconda in ${CONDABASE}" >&2
    $echo "  but failed to find it there." >&2
    $echo "If you know where it is installed," >&2
    $echo "  modify the CONDABASE variable in this script and run it again.">&2
    exit 3
fi

read -p "Shall I update miniconda? If unsure, say yes. [y/n]: " ans
case "$ans" in
Y|y|YES|Yes|yes)
    $conda update conda
    $conda update --all;;
esac
read -p "I'll now install PyFerret. Shall I go ahead? [y/n]: " ans
Y|y|YES|Yes|yes)
  $conda create -n FERRET -c conda-forge pyferret ferret_datasets --yes
*) exit 0
esac

#--- Install pyferret.sh ---
cat > "$wrapper" <<EOF
#!/bin/sh
CONDABASE="$CONDABASE"
EOF
cat >> "$wrapper" <<'EOF'
. $CONDABASE/bin/activate FERRET
#export FER_GO="$FER_GO $HOME/lib/ferret"
#export FER_DATA="$FER_DATA $HOME/lib/ferret"
#export FER_PALETTE="$FER_PALETTE $HOME/lib/ferret/ppl"
exec $CONDABASE/envs/FERRET/bin/pyferret -nojnl "$@"
EOF
$echo "A wrapper script $wrapper has been created."

bindir="$HOME/bin"
$echo "Shall I install $wrapper in your ~/bin/ ?"
read -p "If unsure, say yes. [y/n]: " ans
case "$ans" in
Y|y|YES|Yes|yes) ;;
*) $echo "Okay, I'll leave the script $wrapper here."
   $echo "You may want to copy it to /usr/local/bin or somewhere"
   $echo "  and give it an exec permission by chmod +x $wrapper ."
   exit 0
esac


if [ ! -e "$bindir" ]; then
    mkdir "$bindir" || exit 5
fi
cp "$wrapper" "$bindir/"
chmod +x "$bindir/$wrapper"
$echo "If your PATH doesn't include ~/bin ,"
$echo "  include it by export PATH=\$HOME/bin:\$PATH"
$echo "  in your .bashrc or similar."
$echo "After making this arrangment, log out and log in again,"
$echo "  then, you'll be able to lauch PyFerret just by typing $wrapper "
$echo "  on your command line."
