/^[a-z]/ {
  # if ($1 in dict) 
  #   ++dict[$1]
  # else
  #   dict[$1] = 1
  dict[$1]++
}
END {
  for (keys in dict) 
    printf "%s %d ", keys, dict[keys]
  print ""
}
