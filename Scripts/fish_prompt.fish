function fish_prompt --description 'Informative prompt'
    set -l last_status $status
    echo -n -s -e (set_color brblue)'['(date "+%H:%M:%S")']'(set_color normal)
    echo -n -s -e ' '(set_color brgreen)(pwd)(set_color normal)
    if set -q VIRTUAL_ENV
        echo -n -s -e ' '(set_color bryellow)'('(basename $VIRTUAL_ENV)')'(set_color normal)
    end
    echo -n -s -e (set_color brmagenta)(fish_git_prompt)(set_color normal)
    if test $last_status -ne 0
        echo -n -s -e ' '(set_color brred)'['$last_status']'(set_color normal)
    end
    echo -n -s -e '\n$ '
end
