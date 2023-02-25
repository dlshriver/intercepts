__attribute__((used)) static void *handler(void *self, void *args, void *kwargs)
{
    void *result = ((void *(*)(void *, void *, void *))(0xbbbbbbbbbbbbbbbb))(
        (void *)(0xaaaaaaaaaaaaaaaa),
        args,
        kwargs);

    return result;
}