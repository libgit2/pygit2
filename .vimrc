" pygit2 local vimrc - C extension configuration

" Get Python include path dynamically
let s:python_include = system('python3 -c "import sysconfig; print(sysconfig.get_path(''include''))"')[:-2]

" Configure ALE C linters with proper includes
let g:ale_c_cc_options = '-std=c11 -Wall -I' . s:python_include . ' -I/usr/local/include'
let g:ale_c_gcc_options = '-std=c11 -Wall -I' . s:python_include . ' -I/usr/local/include'
let g:ale_c_clang_options = '-std=c11 -Wall -I' . s:python_include . ' -I/usr/local/include'

" If you have libgit2 in a non-standard location, add it:
" let g:ale_c_cc_options .= ' -I/usr/local/include/git2'

" Optional: Explicitly set which linters to use for C
let g:ale_linters = get(g:, 'ale_linters', {})
let g:ale_linters.c = ['cc', 'clangtidy']  " or ['gcc'] if you prefer
