# VS / Rider 工程模板

把下面的内容存成 `iw-opensource\IwRebuild.csproj`，即可在 IDE 里直接打开、
获得 IntelliSense 与「F5 编译」。

注意两点：

1. `TargetFramework` 用 `net35`（与 Unity 5.6 的 Mono 2.0 对齐）；
2. **不要**让 MSBuild 自动引用框架程序集，必须显式引用 `refs\` 里游戏自带的
   `mscorlib / System / System.Core`，否则运行时会
   `TypeLoadException: Could not load type 'System.Action\`3'`。

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Assembly-CSharp</AssemblyName>
    <TargetFramework>net35</TargetFramework>
    <LangVersion>5</LangVersion>
    <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <NoStdLib>true</NoStdLib>
    <DisableImplicitFrameworkReferences>true</DisableImplicitFrameworkReferences>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <NoWarn>1685</NoWarn>
  </PropertyGroup>

  <ItemGroup>
    <Compile Include="src\**\*.cs" />
  </ItemGroup>

  <ItemGroup>
    <Reference Include="mscorlib">
      <HintPath>refs\mscorlib.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="System">
      <HintPath>refs\System.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="System.Core">
      <HintPath>refs\System.Core.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="System.Xml">
      <HintPath>refs\System.Xml.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="System.Drawing">
      <HintPath>refs\System.Drawing.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="System.Json">
      <HintPath>refs\System.Json.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="UnityEngine">
      <HintPath>refs\UnityEngine.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="UnityEngine.UI">
      <HintPath>refs\UnityEngine.UI.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="UnityEngine.Networking">
      <HintPath>refs\UnityEngine.Networking.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="Assembly-CSharp-firstpass">
      <HintPath>refs\Assembly-CSharp-firstpass.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="HOTween">
      <HintPath>refs\HOTween.dll</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>
</Project>
```

> 本机没有 .NET SDK，所以仓库默认用 `build.cmd`（系统自带 `csc.exe`）。
> 装了 SDK 之后 `dotnet build` 也能用这份 csproj。
