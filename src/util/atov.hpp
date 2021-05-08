namespace atov {
    std::vector<MPlug> convert(MPlugArray& array)
    {
        std::vector<MPlug> result(array.length());

        for (unsigned int i = 0; i < array.length(); i++) {
            result[i] = array[i];
        }

        return result;
    }

    std::vector<std::string> convert(MStringArray& array)
    {
        std::vector<std::string> result(array.length());

        for (unsigned int i = 0; i < array.length(); i++) {
            result[i] = std::string(array[i].asChar());
        }

        return result;
    }
}