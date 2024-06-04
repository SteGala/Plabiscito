# Plabiscito

## How to use 
Plebiscito relies on the functionalities offered by [tcpproxy](https://github.com/ickerwx/tcpproxy).
To add the library first go to the src folder

```
cd src
```

And clone the tcpproxy repository

```
git clone git@github.com:ickerwx/tcpproxy.git
cd tcpproxy
```

Change to a specific brannch (there are no releases available)

```
git checkout ddd487c
```

and the replace the main file with the custom one in the Plebiscito repository

```
cp ../tcpproxy.py .
```