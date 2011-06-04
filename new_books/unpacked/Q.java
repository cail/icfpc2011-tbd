import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.net.JarURLConnection;
import java.net.URL;

class Q
{
  static byte[] r(InputStream paramInputStream)
    throws Throwable
  {
    ByteArrayOutputStream localByteArrayOutputStream = new ByteArrayOutputStream();
    byte[] arrayOfByte = new byte[1024];
    int i;
    while ((i = paramInputStream.read(arrayOfByte)) > 0)
      localByteArrayOutputStream.write(arrayOfByte, 0, i);
    paramInputStream.close();
    return localByteArrayOutputStream.toByteArray();
  }

  static void d(byte[] paramArrayOfByte)
  {
    for (int i = 0; i < paramArrayOfByte.length; i++)
      switch (i & 0x3)
      {
      case 0:
        int tmp42_41 = i; paramArrayOfByte[tmp42_41] = (byte)(paramArrayOfByte[tmp42_41] ^ 0x49); break;
      case 1:
        int tmp54_53 = i; paramArrayOfByte[tmp54_53] = (byte)(paramArrayOfByte[tmp54_53] ^ 0x43); break;
      case 2:
        int tmp66_65 = i; paramArrayOfByte[tmp66_65] = (byte)(paramArrayOfByte[tmp66_65] ^ 0x46); break;
      case 3:
        int tmp78_77 = i; paramArrayOfByte[tmp78_77] = (byte)(paramArrayOfByte[tmp78_77] ^ 0x50);
      }
  }

  static int z(byte[] paramArrayOfByte)
  {
    for (int i = 0; i + 3 < paramArrayOfByte.length; i++)
      if ((paramArrayOfByte[i] == 80) && (paramArrayOfByte[(i + 1)] == 75) && (paramArrayOfByte[(i + 2)] == 3) && (paramArrayOfByte[(i + 3)] == 4))
        return i;
    return paramArrayOfByte.length;
  }

  public static void main(String[] paramArrayOfString)
    throws Throwable
  {
    JarURLConnection localJarURLConnection = (JarURLConnection)Q.class.getResource("Q.class").openConnection();

    byte[] arrayOfByte1 = r(localJarURLConnection.getJarFileURL().openStream());
    byte[] arrayOfByte2 = r(Q.class.getResource("0").openStream());
    byte[] arrayOfByte3 = r(Q.class.getResource("1").openStream());

    int i = z(arrayOfByte1);
    byte[] arrayOfByte4 = arrayOfByte2.length == i ? arrayOfByte3 : arrayOfByte2;
    d(arrayOfByte4);
    System.out.write(arrayOfByte4);
    System.out.write(arrayOfByte1, i, arrayOfByte1.length - i);
  }
}