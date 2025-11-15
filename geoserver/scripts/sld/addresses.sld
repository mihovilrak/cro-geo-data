<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor version="1.0.0"
    xmlns:sld="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.opengis.net/sld
        http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <sld:NamedLayer>
    <sld:Name>addresses</sld:Name>
    <sld:UserStyle>
      <sld:Title>Addresses</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:MaxScaleDenominator>2000</sld:MaxScaleDenominator>

          <sld:TextSymbolizer>
            <sld:Label>
              <ogc:PropertyName>house_number</ogc:PropertyName>
            </sld:Label>

            <sld:Font>
              <sld:CssParameter name="font-family">Arial</sld:CssParameter>
              <sld:CssParameter name="font-size">12</sld:CssParameter>
              <sld:CssParameter name="font-style">Normal</sld:CssParameter>
              <sld:CssParameter name="font-weight">Bold</sld:CssParameter>
            </sld:Font>

            <sld:LabelPlacement>
              <sld:PointPlacement>
                <sld:AnchorPoint>
                  <sld:AnchorPointX>0.5</sld:AnchorPointX>
                  <sld:AnchorPointY>0.5</sld:AnchorPointY>
                </sld:AnchorPoint>
              </sld:PointPlacement>
            </sld:LabelPlacement>

            <sld:Halo>
              <sld:Radius><ogc:Literal>1.5</ogc:Literal></sld:Radius>
              <sld:Fill>
                <sld:CssParameter name="fill">#FFFFFF</sld:CssParameter>
              </sld:Fill>
            </sld:Halo>

            <sld:Fill>
              <sld:CssParameter name="fill">#FF0000</sld:CssParameter>
            </sld:Fill>

            <sld:VendorOption name="autoWrap">60</sld:VendorOption>
            <sld:VendorOption name="spaceAround">1</sld:VendorOption>
            <sld:VendorOption name="maxDisplacement">100</sld:VendorOption>
          </sld:TextSymbolizer>

        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
