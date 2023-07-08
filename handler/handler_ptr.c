__attribute__((section(".text")))
const void *handler_address = (void *)(0xaaaaaaaaaaaaaaaa);
__attribute__((section(".text")))
const void *PyObject_Call_address = (void *)(0xbbbbbbbbbbbbbbbb);
__attribute__((section(".text")))
__attribute__((used)) static void *
handler(void *self, void *args, void *kwargs)
{
    void *result = ((void *(*)(void *, void *, void *))(PyObject_Call_address))(
        (void *)(handler_address),
        args,
        kwargs);

    return result;
}
