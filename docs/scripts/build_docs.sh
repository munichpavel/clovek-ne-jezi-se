# Note: script must be run from docs directory

if [[ "$(basename $PWD)"  = "docs" ]]; then
    make clean-buildapi
    make html

    # Open local index.html in browser
    cd $LOCAL_BUILD_DIR/html
    open ./index.html

    cd -
else
    echo "Aborting: script must be run from docs directory"
    echo "You are in $PWD"
fi