static void *handler(void *self, void *args, void *kwargs)
{

    void *result = ((void *(*)(void *, void *, void *))(0xbbbbbbbbbbbbbbbb))(
        (void *)(0xaaaaaaaaaaaaaaaa),
        args,
        kwargs);

    return result;
}

int main(int argc, char **arg)
{
    return handler(arg[0], arg[1], arg[2]);
}