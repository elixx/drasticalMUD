for file in $(find .  -type f | egrep -v "(\.git)|(\_\_pycache\_\_)|(\.log)|(\.static)|(areas\\bad)|(\.idea) | grep -v settings | grep -v ipynb"); do
  export FILE=$(echo $file | sed 's@\./@@g')
  /usr/bin/rsync -zvar "${FILE}" "${1}/${FILE}"
  #cp -vf "${FILE}" "${1}/${FILE}"
done
